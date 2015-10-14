#include "washington_nodes.h"


//===========================================================================
//===== CONSTRUCTOR and DECONSTRUCTOR =====
//===========================================================================

WashingtonCricketsUnit::WashingtonCricketsUnit():
	CricketsUnit(0, 1, 2, 3, 4, 5)	
{
	
}

WashingtonCricketsUnit::~WashingtonCricketsUnit(){
	
}

void WashingtonCricketsUnit::parse_msg(){

	
	// byte 1 --- type of request
	request_type = recv_data_buff[1];
	
    
	uint16_t temp_val = 0;
	
	switch (request_type){
	
		// Basic
		case 0: { 
		
			// >>>>>> byte 2 to 9: ON-BOARD <<<<<<<
			
			// byte 2 --- indicator led on or off
			indicator_led_on = recv_data_buff[2];

			// byte 3 and 4 --- indicator led blinking frequency	
			temp_val = 0;
			for (uint8_t i = 0; i < 2 ; i++)
			  temp_val += recv_data_buff[3+i] << (8*i);
			indicator_led_blink_period = temp_val;
			
			// >>>> byte 10: CONFIG VARIABLES <<<<<
			
			// byte 10 ---- operation mode
			operation_mode = recv_data_buff[10];
			
			// byte 11 ---- reply message type request
			reply_type = recv_data_buff[11];
			
			// >>>>> byte 30 to byte 39:
			neighbour_activation_state = recv_data_buff[30];
			
			break;
		}
		
		//Teensy programming pin
		case 1: {
			bool program_teensy = recv_data_buff[2];
			if (program_teensy) {
				digitalWrite(PGM_DO_pin, 1);
				digitalWrite(13, 1);
			}
			break;
		}
		
		//Crickets low level requests
		case 2: {
		
			uint8_t  device_offset = 2;

			// (8 bytes each)
			// >>>>> byte 2 to byte 9: Cricket 0
			// >>>>> byte 10 to byte 17: Cricket 1
			// >>>>> byte 18 to byte 25: Cricket 2
			// >>>>> byte 26 to byte 33: Cricket 3
			// >>>>> byte 34 to byte 41: Cricket 4
			// >>>>> byte 41 to byte 49: Cricket 5			
			
			
			for (uint8_t j = 0; j < NUM_CRICKET; j++){
				
				const uint8_t byte_offset = 8*(j) + device_offset;
						
				// byte x0 --- fin SMA wire 0
				cricket_var[j].sma_level[0] = recv_data_buff[byte_offset+0];
				// byte x1 --- fin SMA wire 1
				cricket_var[j].sma_level[1] = recv_data_buff[byte_offset+1];
				// byte x2 --- reflex actuation level
				cricket_var[j].sma_level[2] = recv_data_buff[byte_offset+2];
				// byte x4 --- reflex actuation level
				cricket_var[j].sma_level[3] = recv_data_buff[byte_offset+3];
			
			}
			break;
		
		}
		
		// read-only
		case 255:{
			break;
		}
		default: {
			break;
		}
		

	}

}


//===========================================================================
//====== COMMUNICATION Protocol ======
//===========================================================================

void WashingtonCricketsUnit::compose_reply(byte front_signature, byte back_signature, byte msg_setting){


	// add the signatures to first and last byte
	send_data_buff[0] = front_signature;
	send_data_buff[num_outgoing_byte-1] = back_signature;
		
	if (msg_setting == 0){
		// sample the sensors
		this->sample_inputs();	
	}
	
	// byte 1 --- type of reply
	send_data_buff[1] =  reply_type;	



	switch (reply_type){
	
		case 0:	{
		
						
			break;
		}
		
		// echo
		case 1: {
			
			for (uint8_t i = 2; i<63; i++){

				send_data_buff[i] = recv_data_buff[i];
			}
			break;

		}
		default: {
			break;
		}

	}

		

}

//===========================================================================
//====== Input functions ======
//===========================================================================

//--- Sampling function ---
void WashingtonCricketsUnit::sample_inputs(){

	sample_inputs(0);
}

void WashingtonCricketsUnit::sample_inputs(const uint8_t setting){


}



//===========================================================================
//============ BEHAVIOUR CODES =========
//===========================================================================

//---- inactive behaviour ----
void WashingtonCricketsUnit::inactive_behaviour() {
	
	//=== Cricket ===
	for (uint8_t i=0; i<NUM_CRICKET; i++){
		
		for (uint8_t output_id=0; output_id<4; output_id++){
			cricket[i].set_output_level(output_id, 0);
		}

	}		
		
}

//---- test behaviour ----
void WashingtonCricketsUnit::test_behaviour(const uint32_t &curr_time) {
	
	
	//>>>> Cricket <<<<<

	for (uint8_t i=0; i<NUM_CRICKET; i++){
		
		for (uint8_t output_id=0; output_id<4; output_id++){
			cricket[i].set_output_level(output_id, 255);
		}

	}	
	
	delay(1000);
	for (uint8_t i=0; i<NUM_CRICKET; i++){
		
		for (uint8_t output_id=0; output_id<4; output_id++){
			cricket[i].set_output_level(output_id, 0);
		}

	}	
	delay(4000);
	
}



//---- indicator LED -----

void WashingtonCricketsUnit::led_blink_behaviour(const uint32_t &curr_time) {

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
		indicator_led_blink_cycling = false;

		digitalWrite(indicator_led_pin, 0);
	}
}



//----- LOW-LEVEL CONTROL -------
void WashingtonCricketsUnit::low_level_control_behaviour(){

	
	//>>>> Cricket <<<<<

	for (uint8_t j=0; j<NUM_CRICKET; j++){
		
		for (uint8_t output_id=0; output_id<4; output_id++){
			cricket[j].set_output_level(output_id, cricket_var[j].sma_level[output_id]);
		}

	}	
}
