#include "behaviours.h"


//===========================================================================
//===== CONSTRUCTOR and DECONSTRUCTOR =====
//===========================================================================

Behaviours::Behaviours():
		tentacle_ir_state{tentacle_0_ir_state, tentacle_1_ir_state, tentacle_2_ir_state, tentacle_3_ir_state},
		tentacle_acc_state{tentacle_0_acc_state, tentacle_1_acc_state, tentacle_2_acc_state, tentacle_3_acc_state},
		tentacle_ir_threshold{tentacle_0_ir_threshold, tentacle_1_ir_threshold, tentacle_2_ir_threshold, tentacle_3_ir_threshold},
		tentacle_arm_cycle_period{tentacle_0_arm_cycle_period, tentacle_1_arm_cycle_period , tentacle_2_arm_cycle_period, tentacle_3_arm_cycle_period},
		tentacle_reflex_period{tentacle_0_reflex_period, tentacle_1_reflex_period, tentacle_2_reflex_period, tentacle_3_reflex_period},
		tentacle_sma_level{tentacle_0_sma_level, tentacle_1_sma_level, tentacle_2_sma_level, tentacle_3_sma_level},
		tentacle_motion_on{tentacle_0_motion_on, tentacle_1_motion_on, tentacle_2_motion_on
		
{
	
}

Behaviours::~Behaviours(){
	
}

void Behaviours::parse_msg(){

	uint16_t val = 0;
	
	// byte 1 --- type of request
	request_type = recv_data_buff[1];
        
	switch (request_type){
	
		//Teensy programming pin
		case 1: {
			bool program_teensy = recv_data_buff[2];
			if (program_teensy) {
				digitalWrite(PGM_DO_pin, 1);
				digitalWrite(13, 1);
			}
			break;
		}
		case 2: {
		
			// byte 2 to 33 --- indicator LED wave 
			for (short i = 0; i < wave_size; i++)
				test_wave.waveform[i] = recv_data_buff[i+2];
			break;
		}
		default:{
			// byte 2 --- indicator led on or off
			indicator_led_on = recv_data_buff[2];

			// byte 3 and 4 --- indicator led blinking frequency
			val = 0;
			for (short i = 0; i < 2 ; i++)
			  val += recv_data_buff[i+3] << (8*i);
			//indicator_led_blink_period = val;

			// byte 5 --- high power LED level
			//	high_power_led_level = recv_data_buff[5];
				
			// byte 6 and byte 7 --- high power LED reflex threshold
			val = 0;
			for (short i = 0; i < 2 ; i++)
			  val += recv_data_buff[i+6] << (8*i);
			//high_power_led_reflex_threshold = val;
			
			// byte 8 --- SMA 0 level
			//sma_0_level = recv_data_buff[8];
			
			// byte 9 --- SMA 1 level
			//sma_1_level = recv_data_buff[9];
			
			// byte 10 --- Reflex 0 level
			//reflex_0_level = recv_data_buff[10];
			
			// byte 11 --- Reflex 1 level
			//reflex_1_level = recv_data_buff[11];
			break;
		}
	}

}


//===========================================================================
//====== COMMUNICATION Protocol ======
//===========================================================================

void Behaviours::compose_reply(byte front_signature, byte back_signature){


	// add the signatures to first and last byte
	send_data_buff[0] = front_signature;
	send_data_buff[num_outgoing_byte-1] = back_signature;
	
	// sample the sensors
	this->sample_inputs();
		

	switch (request_type){
	
		default:
			
			// >>> protocell --- byte 1 to 10
			
			send_data_buff[1] =  0;
			send_data_buff[2] =  0;
			
			// >>> tentacle_0 --- byte 11 to 20 
			// >>> tentacle_1 --- byte 21 to 30 
			// >>> tentacle_2 --- byte 31 to 40 
			
			for (uint8_t tentacle_id = 0; tentacle_id<3; tentacle_id++){
			
				// byte *1 and *2 --- ir 0 and ir 1
				send_data_buff[10*tentacle_id + 11] = tentacle_ir_state[tentacle_id][0];
				send_data_buff[10*tentacle_id + 12] = tentacle_ir_state[tentacle_id][1];

			}
		break;
	}

}

//===========================================================================
//====== Input functions ======
//===========================================================================

//--- Sampling function ---
void Behaviours::sample_inputs(){

	const uint8_t read_buff_num = 20;
	//>>>tentacle<<<
	
	//~~IR sensors state~~
	for (uint8_t i = 0; i<3; i++){
		for (uint8_t j=0; j<2; j++){
			uint16_t read_buff = 0;
			for (uint8_t k=0; k<read_buff_num; k++){
				read_buff += tentacle[i].read_analog_state(j);
			}
			tentacle_ir_state[i][j] = (uint8_t) (read_buff/read_buff_num);
		}
	}


	

	if (Wire.frozen){
		//digitalWrite(PGM_DO_pin, 1);
		digitalWrite(13, 1);
	}
		


}

//===========================================================================
//============ BEHAVIOUR CODES =========
//===========================================================================

//---- test behaviour ----
void Behaviours::test_behaviour(const uint32_t &curr_time) {
	
	//=== testing Tentacle ===
	for (uint8_t i=0; i<3; i++){
		uint8_t ir_range = tentacle[i].read_analog_state(0);
		if (ir_range > 100){
			tentacle[i].set_led_level(0, 250);
			tentacle[i].set_led_level(1, 250);
		}
		else{
			tentacle[i].set_led_level(0, 0);
			tentacle[i].set_led_level(1, 0);
		}
		
		ir_range = tentacle[i].read_analog_state(1);
		
		if (ir_range > 100){
			tentacle[i].set_sma_level(0, 250);
			tentacle[i].set_sma_level(1, 250);
			
		}
		else{
			tentacle[i].set_sma_level(0, 0);
			tentacle[i].set_sma_level(1, 0);
		}
	}		
	

	
}

void Behaviours::stress_test_behaviour(const uint32_t &curr_time)
{

	// LED stress test
	static wave_t sine_wave [32] = {127, 151, 175, 197, 216, 232, 244, 251, 254, 251, 244, 232, 216, 197, 175, 151, 127, 102, 78, 56, 37, 21, 9, 2, 0, 2, 9, 21, 37, 56, 78, 102};
	static WaveTable led_wave(1000, sine_wave);
	
	uint8_t led_level = led_wave.wave_function(curr_time);
	
	
	
	//vibration stress test
	for (uint8_t i = 0; i< 3; i++){
		tentacle[i].set_led_level(0, led_level);
		tentacle[i].set_led_level(1, led_level);
	}
	
	// SMA stress test
	//---- Tentacle cycling variables -----
	static bool tentacle_cycling[3] = {false, false, false};
	static uint32_t tentacle_phase_time[3] = {0, 0, 0};
	bool tentacle_on[3] = {false, false, false};
	
	//~~~ tentacle cycle~~~~
	for (uint8_t i=0; i<3; i++){
		
		// starting a cycle
		if (tentacle_cycling[i] == false){
			tentacle_cycling[i] = true;
			tentacle_phase_time[i] = millis();  
			tentacle[i].set_sma_level(0, 255);
			tentacle[i].set_sma_level(1, 255);					
		}
		else if (tentacle_cycling[i] == true){
			
			// if reaches the full period, restart cycle
			if ((curr_time - tentacle_phase_time[i]) > tentacle_cycle_period[i][1]*1000){
				tentacle_cycling[i]  = false;
			}
			// if reaches half the period, turn it off
			else if ((curr_time - tentacle_phase_time[i]) > tentacle_cycle_period[i][0]*1000){
				tentacle[i].set_sma_level(0, 0);
				tentacle[i].set_sma_level(1, 0);
			}	
		}
	}
}


//---- indicator LED -----

void Behaviours::led_blink_behaviour(const uint32_t &curr_time) {

	//---- indicator LED blinking variables -----
	//~~indicator LED on~~
	static bool indicator_led_on_0 = 1;
	//~~indicator LED blink~~
	static bool indicator_led_blink_cycling = false;
	static uint32_t indicator_led_blink_phase_time= 0;

	if (indicator_led_on){
		
		// starting a blink cycle
		if (indicator_led_blink_cycling == false){
			indicator_led_blink_cycling = true;
			indicator_led_blink_phase_time = millis();      
			digitalWrite(indicator_led_pin, 1);
		}
		else if (indicator_led_blink_cycling == true){
			
			// if reaches the full period, restart cycle
			if ((curr_time - indicator_led_blink_phase_time) > indicator_led_blink_period){
				indicator_led_blink_cycling = false;
			}
			// if reaches half the period, turn it off
			else if ((curr_time - indicator_led_blink_phase_time) > indicator_led_blink_period>>1){
				digitalWrite(indicator_led_pin, 0);
			}	
		}
	}
	else{
	
		// if stopped in the middle of a cycle
		if (indicator_led_blink_cycling){
			indicator_led_blink_cycling = false;
			digitalWrite(indicator_led_pin, 0);
		}
	}
}

void Behaviours::led_wave_behaviour(const uint32_t &curr_time){
	
	
	//static WaveTable test_wave(5);
	test_wave.set_duration(10000);
	uint8_t led_level = test_wave.wave_function(curr_time);
	//protocell.set_led_level(led_level);
	analogWrite(5, led_level);
	

}


//---- Tip IR primary action -----
void Behaviours::tentacle_tip_ir_primary_action(const uint32_t &curr_time){
	
	
	//---- Tentacle cycling variables -----
	static bool tentacle_cycling[3] = {false, false, false};
	static uint32_t tentacle_phase_time[3] = {0, 0, 0};
	static bool tentacle_on[3] = {false, false, false};

	//~~read IR sensors state~~
	// for (uint8_t i=0; i<3; i++){
		// tentacle_ir_state[i][1] = tentacle[i].read_analog_state(1);
	// }
	
	static uint16_t sma_offset_time[3] = {0, 0, 0};
	static uint8_t sma0[3] = {0, 0, 0};
	static uint8_t sma1[3] = {1, 1, 1};
	

	
	//~~~ tentacle cycle~~~~
	for (uint8_t i=0; i<3; i++){
	
		
		uint8_t sma_action_type = 0; 
		if (tentacle_ir_state[i][1] > tentacle_ir_threshold[i][1]){
			
			tentacle_on[i] = true;
			
			// determine the adjacent tentacle
			uint8_t adj_id;
			if (i==0){
				adj_id = 2;
			}
			else{
				adj_id = i-1;
			}
			
			
			if (tentacle_ir_state[i][0] > tentacle_ir_threshold[i][0]){
				sma_action_type = 1;
			}
			else if (tentacle_ir_state[adj_id][0] > tentacle_ir_threshold[adj_id][0]){
				sma_action_type = 2;
			}
			
		}

		
		if (tentacle_on[i]){
			
			// starting a cycle
			if (tentacle_cycling[i] == false){
				
				// if setting type to 255, the actual type will be random
				if (sma_action_type == 255){
					sma_action_type = random(0,3);
				}
				// behaviour Type
				switch (sma_action_type){
					case 1:
						sma0[i] = 0;
						sma1[i] = 0;
						sma_offset_time[i] = 0; //tentacle_cycle_offset[i];
					break;
					case 2:
						sma0[i] = 1;
						sma1[i] = 1;
						sma_offset_time[i] = 0; //tentacle_cycle_offset[i];
					break;
					default:
						sma0[i] = 0;
						sma1[i] = 1;
						sma_offset_time[i] = 0;
					break;
				}
				tentacle_cycling[i] = true;
				tentacle_phase_time[i] = millis();  
				
				// turn on the first sma
				tentacle[i].set_sma_level(sma0[i], 255);			
			}
			else if (tentacle_cycling[i] == true){
				
				
				volatile uint32_t cycle_time = curr_time - tentacle_phase_time[i];
				
				// if reaches the full period + offset, restart cycle
				if (cycle_time > (tentacle_cycle_period[i][1]*1000 + sma_offset_time[i])){
					tentacle_cycling[i]  = false;
					tentacle_on[i] = false;
				}
				
				//if reaches the on period + offset time
				else if (cycle_time > (tentacle_cycle_period[i][0]*1000 + sma_offset_time[i])){
					tentacle[i].set_sma_level(sma1[i], 0);
					tentacle[i].set_sma_level(sma0[i], 0);
	
				}
				else{
				
					// if reaches the on period, turn it off
					if (cycle_time > tentacle_cycle_period[i][0]*1000){
						tentacle[i].set_sma_level(sma0[i], 0);
					}	
					

					//if reaches the offset time
					if (cycle_time > sma_offset_time[i]){
						tentacle[i].set_sma_level(sma1[i], 255);
					}
				}
			}
		}

	}
}


// //---- bottom IR primary action  -----
void Behaviours::tentacle_scout_ir_primary_action(const uint32_t &curr_time){


	//---- Tentacle cycling variables -----
	static uint16_t scout_led_period[3] = {preset_scout_led_period[0][0], preset_scout_led_period[1][0], preset_scout_led_period[2][0]};
	static bool scout_led_resting[3] = {true, true, true};
	
	//~~read IR sensors state~~
	// for (uint8_t i=0; i<3; i++){
		// tentacle_ir_state[i][0] = (uint8_t) tentacle[i].read_analog_state(0);
	// }
	
	for (uint8_t i=0; i<3; i++){
		bool scout_led_on = false;
		
		//if something is very close
		if (tentacle_ir_state[i][0] > tentacle_scout_ir_threshold[i][2]){
			scout_led_on = true;
			scout_led_period[i] = preset_scout_led_period[i][2];
			// scout_led_period[i] = (uint16_t) ((int16_t) scout_led_period[i] + 
									// ((int16_t)(preset_scout_led_period[i][2]/period_change_rate) - (int16_t) (scout_led_period[i]/period_change_rate))); 
		
			
		}		

		//if something is close
		else if (tentacle_ir_state[i][0] > tentacle_scout_ir_threshold[i][1]){
			scout_led_on = true;
			scout_led_period[i] = preset_scout_led_period[i][1];
			// scout_led_period[i] = (uint16_t) ((int16_t) scout_led_period[i] + 
									// ((int16_t)(preset_scout_led_period[i][1]/period_change_rate) - (int16_t) (scout_led_period[i]/period_change_rate))); 
			
		
		}

		//if something is detected but far
		else if (tentacle_ir_state[i][0] > tentacle_scout_ir_threshold[i][0]){
			scout_led_on = true;
			scout_led_period[i] = preset_scout_led_period[i][0];
			// scout_led_period[i] = (uint16_t) ((int16_t) scout_led_period[i] + 
									// ((int16_t)(preset_scout_led_period[i][0]/period_change_rate) - (int16_t) (scout_led_period[i]/period_change_rate)));   
	
		}
		
		//if there is no object detected
		else{
			scout_led_on = false;

		}
		
		//Actuation
		
		if (scout_led_on){
			uint8_t scout_led_level = scout_led_wave[i].wave_function(curr_time);
			scout_led_wave[i].set_duration(scout_led_period[i]);
			//uint8_t scout_led_level = scout_led_wave[i].wave_function(curr_time);
			tentacle[i].set_led_level(0, scout_led_level);
			scout_led_resting[i] = false;
		}
		else{
			uint8_t scout_led_level = 0; 
			if (!scout_led_resting[i]){
				scout_led_level = scout_led_wave[i].wave_function(curr_time);
			}

			
			if (scout_led_resting[i] || scout_led_level < 2){
				scout_led_wave[i].restart_wave_function();
				tentacle[i].set_led_level(0, 0);
				scout_led_resting[i] = true;
			}
			else{
				tentacle[i].set_led_level(0, scout_led_level);
				scout_led_resting[i] = false;
			}

		}
		
	}

	
}