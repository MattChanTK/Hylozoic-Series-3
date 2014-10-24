#include "HK_behaviours.h"


//===========================================================================
//===== CONSTRUCTOR and DECONSTRUCTOR =====
//===========================================================================

HK_Behaviours::HK_Behaviours():
		tentacle_ir_state{tentacle_0_ir_state, tentacle_1_ir_state, tentacle_2_ir_state},
		tentacle_ir_threshold{tentacle_0_ir_threshold, tentacle_1_ir_threshold, tentacle_2_ir_threshold},
		tentacle_cycle_period{tentacle_0_cycle_period, tentacle_1_cycle_period , tentacle_2_cycle_period},
		tentacle_scout_ir_threshold{tentacle_0_scout_ir_threshold, tentacle_1_scout_ir_threshold, tentacle_2_scout_ir_threshold},
		scout_led_0_wave(5000, cos_wave_1),
		scout_led_1_wave(5000, cos_wave_1),
		scout_led_2_wave(5000, cos_wave_1),
		scout_led_wave{scout_led_0_wave, scout_led_1_wave, scout_led_2_wave},
		extra_lights_0_wave(2500, cos_wave_1),
		extra_lights_1_wave(2500, cos_wave_2),
		extra_lights_2_wave(2500, cos_wave_3),
		extra_lights_3_wave(2500, cos_wave_4),
		extra_lights_wave{extra_lights_0_wave, extra_lights_1_wave, extra_lights_2_wave, extra_lights_3_wave}
		
{
	
}

HK_Behaviours::~HK_Behaviours(){
	
}

void HK_Behaviours::parse_msg(){

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

void HK_Behaviours::compose_reply(byte front_signature, byte back_signature){


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
void HK_Behaviours::sample_inputs(){

	
	//>>>tentacle<<<
	
	//~~IR sensors state~~
	for (uint8_t i=0; i<2; i++){
		tentacle_ir_state[0][i] = tentacle_0.read_analog_state(i);
		tentacle_ir_state[1][i] = tentacle_1.read_analog_state(i);
		tentacle_ir_state[2][i] = tentacle_2.read_analog_state(i);
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
void HK_Behaviours::test_behaviour(const uint32_t &curr_time) {
	
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
	
	//=== testing extra lights ===
	uint8_t ir_range = tentacle[0].read_analog_state(0);
	if (ir_range > 100){
		extra_lights.set_led_level(0, 250);	
		extra_lights.set_led_level(1, 250);	
		extra_lights.set_sma_level(0, 250);	
		extra_lights.set_sma_level(1, 250);	
	}
	else{
		extra_lights.set_led_level(0, 0);	
		extra_lights.set_led_level(1, 0);	
		extra_lights.set_sma_level(0, 0);	
		extra_lights.set_sma_level(1, 0);	
	}
	
}

void HK_Behaviours::stress_test_behaviour(const uint32_t &curr_time)
{

	// LED stress test
	static wave_t sine_wave [32] = {127, 151, 175, 197, 216, 232, 244, 251, 254, 251, 244, 232, 216, 197, 175, 151, 127, 102, 78, 56, 37, 21, 9, 2, 0, 2, 9, 21, 37, 56, 78, 102};
	static WaveTable led_wave(1000, sine_wave);
	
	uint8_t led_level = led_wave.wave_function(curr_time);
	
	extra_lights.set_led_level(0, led_level);
	extra_lights.set_led_level(1, led_level);
	extra_lights.set_sma_level(0, led_level);
	extra_lights.set_sma_level(1, led_level);
	
	
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

void HK_Behaviours::led_blink_behaviour(const uint32_t &curr_time) {

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

void HK_Behaviours::led_wave_behaviour(const uint32_t &curr_time){
	
	
	//static WaveTable test_wave(5);
	test_wave.set_duration(10000);
	uint8_t led_level = test_wave.wave_function(curr_time);
	//protocell.set_led_level(led_level);
	analogWrite(5, led_level);
	

}


//---- Tip IR primary action -----
void HK_Behaviours::tentacle_tip_ir_primary_action(const uint32_t &curr_time, const uint8_t* type){
	
	
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
	
		
		if (tentacle_ir_state[i][1] > tentacle_ir_threshold[i][1]){
			tentacle_on[i] = true;
		}

		
		if (tentacle_on[i]){
			
			// starting a cycle
			if (tentacle_cycling[i] == false){
				
				uint8_t sma_action_type = type[i];
				// if setting type to 255, the actual type will be random
				if (sma_action_type == 255){
					sma_action_type = random(0,3);
				}
				// behaviour Type
				switch (sma_action_type){
					case 1:
						sma0[i] = 0;
						sma1[i] = 1;
						sma_offset_time[i] = tentacle_cycle_offset[i];
					break;
					case 2:
						sma0[i] = 1;
						sma1[i] = 0;
						sma_offset_time[i] = tentacle_cycle_offset[i];
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
				
				// if reaches the on period, turn it off
				else if (cycle_time > tentacle_cycle_period[i][0]*1000){
					tentacle[i].set_sma_level(sma0[i], 0);
				}	
				

				//if reaches the offset time
				else if (cycle_time > sma_offset_time[i]){
					tentacle[i].set_sma_level(sma1[i], 255);
				}
			}
		}

	}
}


// //---- bottom IR primary action  -----
void HK_Behaviours::tentacle_scout_ir_primary_action(const uint32_t &curr_time){


	//---- Tentacle cycling variables -----
	static uint16_t scout_led_period[3] = {5000, 5000, 5000};
	static uint16_t extra_lights_period[4] = {2500, 2500, 2500, 2500};
	

	//~~read IR sensors state~~
	// for (uint8_t i=0; i<3; i++){
		// tentacle_ir_state[i][0] = (uint8_t) tentacle[i].read_analog_state(0);
	// }
	
	bool extra_lights_on = false;
	
	for (uint8_t i=0; i<3; i++){
		bool scout_led_on = false;

		//if something is very close
		if (tentacle_ir_state[i][0] > tentacle_scout_ir_threshold[i][2]){
			scout_led_on = true;
			scout_led_period[i] = 1000;
			
			extra_lights_on = true;
			if (extra_lights_on){
				for (uint8_t j=0; j<4; j++){
					if (extra_lights_period[j] > 1000){
						extra_lights_period[j] = 1000;
					}
				}
			}
			
		}		

		//if something is close
		else if (tentacle_ir_state[i][0] > tentacle_scout_ir_threshold[i][1]){
			scout_led_on = true;
			scout_led_period[i] = 5000;
			
			extra_lights_on = true;
			if (extra_lights_on){
				for (uint8_t j=0; j<4; j++){
					if (extra_lights_period[j] > 2500){
						extra_lights_period[j] = 2500;
					}
				}
			}
		}

		//if something is detected but far
		else if (tentacle_ir_state[i][0] > tentacle_scout_ir_threshold[i][0]){
			scout_led_on = true;
			scout_led_period[i] = 5000;
			
			extra_lights_on |= false;
			
			
		}
		
		//if there is no object detected
		else{
			scout_led_on = false;
			extra_lights_on |= false;
		}
		
		if (scout_led_on){
			scout_led_wave[i].set_duration(scout_led_period[i]);
			uint8_t scout_led_level = scout_led_wave[i].wave_function(curr_time);
			
			tentacle[i].set_led_level(0, scout_led_level);
		}
		else{
			scout_led_wave[i].restart_wave_function();
			tentacle[i].set_led_level(0, 0);

		}
		
	}


	if (extra_lights_on){

		for (uint8_t i=0; i<4; i++){
			extra_lights_wave[i].set_duration(extra_lights_period[i]);
			uint8_t extra_lights_level = extra_lights_wave[i].wave_function(curr_time);
			
			if (i<2){
				extra_lights.set_led_level(i, extra_lights_level);
			}
			else{
				extra_lights.set_sma_level(i-2, extra_lights_level);
			}
		}
	}
	else{
		for (uint8_t i=0; i<4; i++){
			extra_lights_wave[i].restart_wave_function();
			uint8_t extra_lights_level = 0;
			extra_lights_period[i] =25000;
			
			if (i<2){
				extra_lights.set_led_level(i, extra_lights_level);
			}
			else{
				extra_lights.set_sma_level(i-2, extra_lights_level);
			}
		}
			
	}
	
}