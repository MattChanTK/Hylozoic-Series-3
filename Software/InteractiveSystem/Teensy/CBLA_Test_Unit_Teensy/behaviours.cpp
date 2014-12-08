#include "behaviours.h"


//===========================================================================
//===== CONSTRUCTOR and DECONSTRUCTOR =====
//===========================================================================

Behaviours::Behaviours()	
{
	
}

Behaviours::~Behaviours(){
	
}

void Behaviours::parse_msg(){

	
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
			for (uint8_t i = 0; i < wave_size; i++)
				test_wave.waveform[i] = recv_data_buff[i+2];
			break;
		}
		default:{
		
			// >>>>>> byte 2 to 9: ON-BOARD <<<<<<<
			
			// byte 2 --- indicator led on or off
			indicator_led_on = recv_data_buff[2];

			// byte 3 and 4 --- indicator led blinking frequency
					
			for (uint8_t i = 0; i < 2 ; i++)
			  indicator_led_blink_period += recv_data_buff[3+i] << (8*i);
			
			
			// >>>>> byte 10 to byte 19: TENTACLE 0
			// >>>>> byte 20 to byte 29: TENTACLE 1
			// >>>>> byte 30 to byte 39: TENTACLE 2		
			for (uint8_t j = 0; j < 4; j++){
				
				uint8_t byte_offset = 10*(j) + 10;
				
				// byte x0 --- IR 0 sensor state
				for (uint8_t i = 0; i < 2; i++)
					tentacle_var[j].tentacle_ir_state[0] += recv_data_buff[byte_offset+i] << (8*i);
					
				// byte x2 --- IR 1 sensor state
				for (uint8_t i = 0; i < 2; i++)
					tentacle_var[j].tentacle_ir_state[1] += recv_data_buff[byte_offset+2+i] << (8*i);
					
				// byte x4 -- Accelerometer state (x-axis)
				for (uint8_t i = 0; i < 2; i++)
					tentacle_var[j].tentacle_acc_state[0] += recv_data_buff[byte_offset+4+i] << (8*i);
					
				// byte x6 -- Accelerometer state (y-axis)
				for (uint8_t i = 0; i < 2; i++)
					tentacle_var[j].tentacle_acc_state[1] += recv_data_buff[byte_offset+6+i] << (8*i);
				
				// byte x8 -- Accelerometer state (z-axis)
				for (uint8_t i = 0; i < 2; i++)
					tentacle_var[j].tentacle_acc_state[2] += recv_data_buff[byte_offset+8+i] << (8*i);			

			}
			
			
			// >>>>> byte 40 to byte 49: Protocell 0 and 1
		
			// byte 40 --- ambient light sensor 0 state
			for (uint8_t i = 0; i < 2; i++)
				protocell_var[0].protocell_als_state += recv_data_buff[40+i] << (8*i);
				
			// byte 42 --- ambient light sensor 1 state
			for (uint8_t i = 0; i < 2; i++)
				protocell_var[1].protocell_als_state += recv_data_buff[42+i] << (8*i);
					
			
			
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
		{
		
			// byte 1 --- type of reply
			recv_data_buff[1] = reply_type;		

			switch (reply_type){
			
				default:
				{
					// >>>>> byte 10 to byte 19: TENTACLE 0
					// >>>>> byte 20 to byte 29: TENTACLE 1
					// >>>>> byte 30 to byte 39: TENTACLE 2		
						
					for (uint8_t j = 0; j < 4; j++){
						
						uint8_t byte_offset = 10*(j) + 10;
						
						// byte x0 --- IR 0 sensor state
						for (uint8_t i = 0; i < 2; i++)
							recv_data_buff[byte_offset+0+i] = tentacle_var[j].tentacle_ir_state[0] >> (8*i); 
						
						// byte x2 --- IR 1 sensor state
						for (uint8_t i = 0; i < 2; i++)
							recv_data_buff[byte_offset+2+i] = tentacle_var[j].tentacle_ir_state[1] >> (8*i); 
				
							
						// byte x4 -- Accelerometer state (x-axis)
						for (uint8_t i = 0; i < 2; i++)
							recv_data_buff[byte_offset+4+i] = tentacle_var[j].tentacle_acc_state[0] >> (8*i); 
					
						// byte x6 -- Accelerometer state (y-axis)
						for (uint8_t i = 0; i < 2; i++)
							recv_data_buff[byte_offset+6+i] = tentacle_var[j].tentacle_acc_state[1] >> (8*i); 
						
						// byte x8 -- Accelerometer state (z-axis)
						for (uint8_t i = 0; i < 2; i++)
							recv_data_buff[byte_offset+8+i] = tentacle_var[j].tentacle_acc_state[2] >> (8*i); 
			
					}
					
					
					// >>>>> byte 40 to byte 49: Protocell 0 and 1
				
					// byte 40 --- ambient light sensor 0 state
					for (uint8_t i = 0; i < 2; i++)
						recv_data_buff[40+i] = protocell_var[0].protocell_als_state >> (8*i); 
						
					// byte 42 --- ambient light sensor 1 state
					for (uint8_t i = 0; i < 2; i++)
						recv_data_buff[42+i] = protocell_var[1].protocell_als_state >> (8*i);
					
					// >>>>> byte 50 to byte 59:
					recv_data_buff[50] = neighbour_activation_state; 
				}		
				break;


			}
		}
		break;
	}

}

//===========================================================================
//====== Input functions ======
//===========================================================================

//--- Sampling function ---
void Behaviours::sample_inputs(){

	// const uint8_t read_buff_num = 20;
	// //>>>tentacle<<<
	
	// //~~IR sensors state~~
	// for (uint8_t i = 0; i<3; i++){
		// for (uint8_t j=0; j<2; j++){
			// uint16_t read_buff = 0;
			// for (uint8_t k=0; k<read_buff_num; k++){
				// read_buff += tentacle[i].read_analog_state(j);
			// }
			// tentacle_ir_state[i][j] = (uint8_t) (read_buff/read_buff_num);
		// }
	// }


	

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


