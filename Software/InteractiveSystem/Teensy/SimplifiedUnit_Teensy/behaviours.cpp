#include "behaviours.h"


//===========================================================================
//===== CONSTRUCTOR and DECONSTRUCTOR =====
//===========================================================================

Behaviours::Behaviours():
		tentacle_ir_state{tentacle_0_ir_state, tentacle_1_ir_state, tentacle_2_ir_state},
		tentacle_acc_state{tentacle_0_acc_state, tentacle_1_acc_state,tentacle_2_acc_state}
{

}

Behaviours::~Behaviours(){
	
}

void Behaviours::parse_msg(){

	uint16_t val = 0;
	
	// byte 1 --- type of request
	request_type = recv_data_buff[1];
        
	switch (request_type){
		case 1: {
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
			indicator_led_blink_period = val;

			// byte 5 --- high power LED level
			high_power_led_level = recv_data_buff[5];
				
			// byte 6 and byte 7 --- high power LED reflex threshold
			val = 0;
			for (short i = 0; i < 2 ; i++)
			  val += recv_data_buff[i+6] << (8*i);
			high_power_led_reflex_threshold = val;
			
			// byte 8 --- SMA 0 level
			sma_0_level = recv_data_buff[8];
			
			// byte 9 --- SMA 1 level
			sma_1_level = recv_data_buff[9];
			
			// byte 10 --- Reflex 0 level
			reflex_0_level = recv_data_buff[10];
			
			// byte 11 --- Reflex 1 level
			reflex_1_level = recv_data_buff[11];
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
			
			send_data_buff[1] = protocell_ambient_light_sensor_state;
			
			
			// >>> tentacle_0 --- byte 11 to 20 
			// >>> tentacle_1 --- byte 21 to 30 
			// >>> tentacle_2 --- byte 31 to 40 
			
			for (uint8_t tentacle_id = 0; tentacle_id<3; tentacle_id++){
			
				// byte *1 and *2 --- ir 0 and ir 1
				send_data_buff[10*tentacle_id + 11] = tentacle_ir_state[0][0];
				send_data_buff[10*tentacle_id + 12] = tentacle_ir_state[0][1];
				
				// byte *3 and *4 --- acc x
				for (uint8_t i = 0; i < 2 ; i++)
					send_data_buff[10*tentacle_id+13+i] = tentacle_acc_state[tentacle_id][0] >> (8*i);
					
				for (uint8_t i = 0; i < 2 ; i++)
				// byte *5 and *6 --- acc y
					send_data_buff[10*tentacle_id+15+i] = tentacle_acc_state[tentacle_id][1] >> (8*i);
					
				// byte *7 and *8 --- acc z
				for (uint8_t i = 0; i < 2 ; i++)
					send_data_buff[10*tentacle_id+17+i] = tentacle_acc_state[tentacle_id][2] >> (8*i);

			}
		break;
	}

}

//===========================================================================
//====== Input functions ======
//===========================================================================

//--- Sampling function ---
void Behaviours::sample_inputs(){

	//>>>protocell<<<
	protocell_ambient_light_sensor_state = protocell.read_analog_state();
	
	//>>>tentacle<<<
	
	//~~IR sensors state~~
	for (uint8_t i=0; i<3; i++){
		tentacle_ir_state[0][i] = tentacle_0.read_analog_state(i);
		tentacle_ir_state[1][i] = tentacle_1.read_analog_state(i);
		tentacle_ir_state[2][i] = tentacle_2.read_analog_state(i);
	}
	
	//~~accelerator~~
	tentacle_0.read_acc_state(tentacle_acc_state[0][0], tentacle_acc_state[0][1], tentacle_acc_state[0][2]);
	tentacle_1.read_acc_state(tentacle_acc_state[1][0], tentacle_acc_state[1][1], tentacle_acc_state[1][2]);
	tentacle_2.read_acc_state(tentacle_acc_state[2][0], tentacle_acc_state[2][1], tentacle_acc_state[2][2]);

}

//===========================================================================
//============ BEHAVIOUR CODES =========
//===========================================================================

//---- test behaviour ----
void Behaviours::test_behaviour(const uint32_t &curr_time) {
	
	//=== testing protocells =====
	uint8_t light_level = protocell.read_analog_state();
	
	if (light_level < 20)
		protocell.set_led_level(5);
	else
		protocell.set_led_level(0);
		
	//=== testing Tentacle ===
	tentacle_0.set_led_level(0, 250);
		
	
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
	test_wave.set_pin_num(tentacle_1.led_pins[1]);
	//test_wave.set_pin_num(FPWM_pin[1][1]);
	test_wave.set_duration(10000);
	test_wave.set_amplitude(1.0);
	test_wave.wave_function(curr_time);
	//tentacle_1.set_led_level(1, 255);
	

}

//----- Protocell reflex -----
void Behaviours::protocell_reflex(const uint32_t &curr_time){
	//----- Protocell reflex -----
	static bool high_power_led_cycling = false;
	static uint32_t protocell_reflex_phase_time= 0;

}

//--- Tentacle reflex ----
void Behaviours::tentacle_reflex(const uint32_t &curr_time){
	//--- Tentacle reflex ----
	static bool tentacle_reflex_cycling = false;
	static uint32_t tentacle_reflex_phase_time = 0;
}




