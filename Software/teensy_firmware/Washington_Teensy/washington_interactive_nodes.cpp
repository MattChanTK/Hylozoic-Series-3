#include "washington_interactive_nodes.h"


//===========================================================================
//===== CONSTRUCTOR and DECONSTRUCTOR =====
//===========================================================================

WashingtonCricketNode::WashingtonCricketNode(uint8_t cricket0_port_id, 
											   uint8_t cricket1_port_id, 
											   uint8_t cricket2_port_id,
											   uint8_t light0_port_id
											   ):
	CricketsLightsUnit(cricket0_port_id, cricket1_port_id, cricket2_port_id, light0_port_id)	
{
	
}

WashingtonCricketNode::~WashingtonCricketNode(){
	
}

void WashingtonCricketNode::parse_msg(){

	
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
			
			
			for (uint8_t j = 0; j < NUM_CRICKET; j++){
				
				const uint8_t byte_offset = 8*(j) + device_offset;
						
				// byte x0 --- actuator 0 level
				cricket_var[j].output_level[0] = recv_data_buff[byte_offset+0];
				// byte x1 --- actuator 1 level
				cricket_var[j].output_level[1] = recv_data_buff[byte_offset+1];
				// byte x2 --- actuator 2 level
				cricket_var[j].output_level[2] = recv_data_buff[byte_offset+2];
				// byte x4 --- actuator 3 level
				cricket_var[j].output_level[3] = recv_data_buff[byte_offset+3];
			
			}
			
			device_offset += 8*NUM_CRICKET;

			// (8 bytes each)
			// >>>>> byte 26 to byte 33: Light 0		
			
			
			for (uint8_t j = 0; j < NUM_LIGHT; j++){
				
				const uint8_t byte_offset = 8*(j) + device_offset;
						
				// byte x0 --- LED 0 level
				light_var[j].led_level[0] = recv_data_buff[byte_offset+0];
				// byte x1 --- LED 1 level
				light_var[j].led_level[1] = recv_data_buff[byte_offset+1];
				// byte x2 --- LED 2 level
				light_var[j].led_level[2] = recv_data_buff[byte_offset+2];
				// byte x4 --- LED 3 level
				light_var[j].led_level[3] = recv_data_buff[byte_offset+3];
			
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

void WashingtonCricketNode::compose_reply(byte front_signature, byte back_signature, byte msg_setting){


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
			
			uint8_t  device_offset = 2;
			
			// (8 bytes each)
			// >>>>> byte 2 to byte 9: Cricket 0
			// >>>>> byte 10 to byte 17: Cricket 1
			// >>>>> byte 18 to byte 25: Cricket 2		
				
			for (uint8_t j = 0; j < NUM_CRICKET; j++){
				
				const uint8_t byte_offset = 8*(j) + device_offset;
				
				// byte x0 --- IR 0 sensor state
				for (uint8_t i = 0; i < 2; i++)
					send_data_buff[byte_offset+0+i] = cricket_var[j].ir_state >> (8*i); 
				
	
			}
			
			device_offset += 8*NUM_CRICKET;
			
			// (8 bytes each)
			// >>>>> byte 26 to byte 33: Light 0	
			
			for (uint8_t j = 0; j < NUM_LIGHT; j++){
				
				const uint8_t byte_offset = 8*(j) + device_offset;
				
				// byte x0 --- IR 0
				for (uint8_t i = 0; i < 2; i++)
					send_data_buff[byte_offset+0+i] = light_var[j].ir_state[0] >> (8*i); 
				
				// byte x2 --- IR 1
				for (uint8_t i = 0; i < 2; i++)
					send_data_buff[byte_offset+2+i] = light_var[j].ir_state[1] >> (8*i); 
			}
				
			
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
void WashingtonCricketNode::sample_inputs(){

	sample_inputs(0);
}

void WashingtonCricketNode::sample_inputs(const uint8_t setting){


}



//===========================================================================
//============ BEHAVIOUR CODES =========
//===========================================================================

//---- inactive behaviour ----
void WashingtonCricketNode::inactive_behaviour() {
	
	//=== Cricket ===
	for (uint8_t i=0; i<NUM_CRICKET; i++){
		
		for (uint8_t output_id=0; output_id<4; output_id++){
			cricket[i].set_output_level(output_id, 0);
		}

	}		
		
}

//---- test behaviour ----
void WashingtonCricketNode::test_behaviour(const uint32_t &curr_time) {
	
	
	//>>>> Cricket <<<<<

	for (uint8_t i=0; i<NUM_CRICKET; i++){
		uint16_t ir_range = cricket[i].read_analog_state(0);
		if (ir_range > 1200){
			for (uint8_t output_id=0; output_id<4; output_id++){
				cricket[i].set_output_level(output_id, 255);
			}
		}
		else{
			for (uint8_t output_id=0; output_id<4; output_id++){
				cricket[i].set_output_level(output_id, 0);
			}
			
		}

	}	
	
	//>>>> Light <<<<<

	for (uint8_t i=0; i<NUM_LIGHT; i++){
		uint16_t ir_range = light[i].read_analog_state(0);
		if (ir_range > 1200){
			for (uint8_t output_id=0; output_id<4; output_id++){
				light[i].set_output_level(output_id, 255);
			}
		}
		else{
			for (uint8_t output_id=0; output_id<4; output_id++){
				light[i].set_output_level(output_id, 0);
			}
			
		}

	}	

	
}



//---- indicator LED -----

void WashingtonCricketNode::led_blink_behaviour(const uint32_t &curr_time) {

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
void WashingtonCricketNode::low_level_control_behaviour(){

	
	//>>>> Cricket <<<<<

	for (uint8_t j=0; j<NUM_CRICKET; j++){
		
		for (uint8_t output_id=0; output_id<4; output_id++){
			cricket[j].set_output_level(output_id, cricket_var[j].output_level[output_id]);
		}

	}

	//>>>> Light <<<<<

	for (uint8_t j=0; j<NUM_LIGHT; j++){
		
		for (uint8_t output_id=0; output_id<4; output_id++){
			light[j].set_output_level(output_id, light_var[j].led_level[output_id]);
		}

	}		
}
