#include "washington_interactive_nodes.h"


//===========================================================================
//===== Washington Fin Cricket Node =====
//===========================================================================

WashingtonCricketNode::WashingtonCricketNode(uint8_t cricket0_port_id, 
											   uint8_t cricket1_port_id, 
											   uint8_t cricket2_port_id,
											   uint8_t light0_port_id
											   ):
	CricketsLightsUnit(cricket0_port_id, cricket1_port_id, cricket2_port_id, light0_port_id)	
{
	//Serial.println("This is a Washington Cricket Node");
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
			// ==== Crickets ====
			// (8 bytes each)
			// >>>>> byte 2 to byte 9: Cricket 0
			// >>>>> byte 10 to byte 17: Cricket 1
			// >>>>> byte 18 to byte 25: Cricket 2			
			
			
			for (uint8_t j = 0; j < WashingtonCricketNode::NUM_CRICKET; j++){
				
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
			
			device_offset += 8*WashingtonCricketNode::NUM_CRICKET;

			// ==== Lights ====
			// (8 bytes each)
			// >>>>> byte 26 to byte 33: Light 0		
			
			
			for (uint8_t j = 0; j < WashingtonCricketNode::NUM_LIGHT; j++){
				
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



//====== COMMUNICATION Protocol ======

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
			// ==== Crickets ====

			// (8 bytes each)
			// >>>>> byte 2 to byte 9: Cricket 0
			// >>>>> byte 10 to byte 17: Cricket 1
			// >>>>> byte 18 to byte 25: Cricket 2		
				
			for (uint8_t j = 0; j < WashingtonCricketNode::NUM_CRICKET; j++){
				
				const uint8_t byte_offset = 8*(j) + device_offset;
				
				// byte x0 --- IR 0 sensor state
				for (uint8_t i = 0; i < 2; i++)
					send_data_buff[byte_offset+0+i] = cricket_var[j].ir_state >> (8*i); 
				
	
			}
			
			device_offset += 8*WashingtonCricketNode::NUM_CRICKET;
			
			// ==== Lights ====

			// (8 bytes each)
			// >>>>> byte 26 to byte 33: Light 0	
			
			for (uint8_t j = 0; j < WashingtonCricketNode::NUM_LIGHT; j++){
				
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

//====== Input functions ======


//--- Sampling function ---
void WashingtonCricketNode::sample_inputs(){

	sample_inputs(0);
}

void WashingtonCricketNode::sample_inputs(const uint8_t setting){
	
	//=== Cricket ===
	for (uint8_t j=0; j<WashingtonCricketNode::NUM_CRICKET; j++){
	
		//~~IR sensors state~~
		noInterrupts();
		cricket_var[j].ir_state = cricket[j].read_analog_state(0);
		interrupts();
		
	}
	
	//=== Light ===
	for (uint8_t j=0; j<WashingtonCricketNode::NUM_LIGHT; j++){
	
		//~~IR sensors state~~
		for (uint8_t i=0; i<2; i++){
			noInterrupts();
			light_var[j].ir_state[i] = light[j].read_analog_state(i);
			interrupts();
		}
	}

}




//============ BEHAVIOUR CODES =========


//---- inactive behaviour ----
void WashingtonCricketNode::inactive_behaviour() {
	
	//=== Cricket ===
	for (uint8_t i=0; i<WashingtonCricketNode::NUM_CRICKET; i++){
		
		for (uint8_t output_id=0; output_id<4; output_id++){
			cricket[i].set_output_level(output_id, 0);
		}

	}	

	//=== Light ===
	for (uint8_t i=0; i<WashingtonCricketNode::NUM_LIGHT; i++){
		
		for (uint8_t output_id=0; output_id<4; output_id++){
			light[i].set_output_level(output_id, 0);
		}

	}		
		
}

//---- test behaviour ----
void WashingtonCricketNode::test_behaviour(const uint32_t &curr_time) {

	
	//>>>> Cricket <<<<<
	for (uint8_t j=0; j<WashingtonCricketNode::WashingtonCricketNode::NUM_CRICKET; j++){
		// Serial.print(j);
		// Serial.print(": ");
		// Serial.println(cricket_var[j].ir_state );
		// for (uint8_t output_id=0; output_id<4; output_id++){
			// cricket[j].set_output_level(output_id, 50);
		// }
		
	
		if (cricket_var[j].ir_state > 1200){
			
			for (uint8_t output_id=0; output_id<4; output_id++){
				cricket[j].set_output_level(output_id, 100);
			}
		}
		else{
			for (uint8_t output_id=0; output_id<4; output_id++){
				cricket[j].set_output_level(output_id, 0);
			}
			
		}

	}	
	
	//>>>> Light <<<<<

	for (uint8_t j=0; j<WashingtonCricketNode::WashingtonCricketNode::NUM_LIGHT; j++){
		// for (uint8_t output_id=0; output_id<4; output_id++){
			// light[j].set_output_level(output_id, 50);
		// }
		if (light_var[j].ir_state[0] > 1200){
			light[j].set_output_level(0, 100);
			light[j].set_output_level(2, 100);
		}
		else{
			light[j].set_output_level(0, 0);
			light[j].set_output_level(2, 0);
		}
		if (light_var[j].ir_state[1] > 1200){
			light[j].set_output_level(1, 100);
			light[j].set_output_level(3, 100);
		}
		else{
			light[j].set_output_level(1, 0);
			light[j].set_output_level(3, 0);
		}

	}	

	
}

//---- self_running_behaviour ----
void WashingtonCricketNode::self_running_behaviour(const uint32_t &curr_time) {
	
	static const uint16_t cricket_max_level = 150;
	static const uint16_t light_max_level = 255;

	//>>>> Cricket <<<<<
	for (uint8_t j=0; j<WashingtonCricketNode::NUM_CRICKET; j++){
		
		// starting a cycle
		if (cricket_var[j].ir_state > 1200 && !cricket_var[j].cycling){
			Serial.println("starting cycle");
			cricket_var[j].cycling = true; 
			cricket_var[j].phase_time = millis();  	
			cricket_var[j].step_time = millis();
			cricket_var[j].next_step_time = 1;
		}
		else if (cricket_var[j].cycling) {
						
			volatile uint32_t cycle_time = curr_time - cricket_var[j].phase_time;

			//ramping down
			// if reaches the full period, restart cycle
			if (cycle_time > 4000){
				
				volatile uint32_t ramping_time = curr_time - cricket_var[j].step_time;
				
				if (ramping_time > cricket_var[j].next_step_time){
					for (uint8_t output_id=0; output_id<4; output_id++){
						if (cricket_var[j].output_level[output_id] > 0) 
							cricket_var[j].output_level[output_id] -= 1;
					}
					cricket_var[j].next_step_time += 1;
					cricket_var[j].step_time = millis();
				}
				
				bool end_cycling = true;
				for (uint8_t output_id=0; output_id<4; output_id++){
					end_cycling &= cricket_var[j].output_level[output_id] <= 0 ;
				}
				if (end_cycling){
					cricket_var[j].cycling = 0;
				}
				
			}
			//hold steady
			else if (cycle_time > 3000){
				
			}
			// ramping up
			else{
				volatile uint32_t ramping_time = curr_time - cricket_var[j].step_time;
				
				if (ramping_time > cricket_var[j].next_step_time){
					for (uint8_t output_id=0; output_id<4; output_id++){
						if (cricket_var[j].output_level[output_id] < cricket_max_level) 
							cricket_var[j].output_level[output_id] += 1;
					}
					if (cricket_var[j].output_level[0] < cricket_max_level) 
							cricket_var[j].output_level[0] += 1;
		
					if (cycle_time > 500){
						if (cricket_var[j].output_level[1] < cricket_max_level) 
							cricket_var[j].output_level[1] += 1;
					}
					if (cycle_time > 1000){
						if (cricket_var[j].output_level[2] < cricket_max_level) 
							cricket_var[j].output_level[2] += 1;
					}
					if (cycle_time > 1500){
						if (cricket_var[j].output_level[3] < cricket_max_level) 
							cricket_var[j].output_level[3] += 1;
					}
					cricket_var[j].next_step_time += 1;
					cricket_var[j].step_time = millis();  	
				}
			
			}				
		}
	}
	//>>>> Light <<<<<
	for (uint8_t j=0; j<WashingtonCricketNode::NUM_LIGHT; j++){
		
		// starting a cycle
		if ((light_var[j].ir_state[0] > 1200 || light_var[j].ir_state[1] > 1200) && !light_var[j].cycling){
			Serial.println("starting cycle");
			light_var[j].cycling = true; 
			light_var[j].phase_time = millis();  	
			light_var[j].step_time = millis();
			light_var[j].next_step_time = 20;
		}
		else if (light_var[j].cycling) {
						
			volatile uint32_t cycle_time = curr_time - light_var[j].phase_time;

			//ramping down
			// if reaches the full period, restart cycle
			if (cycle_time > 4000){
				
				volatile uint32_t ramping_time = curr_time - light_var[j].step_time;
				
				if (ramping_time > light_var[j].next_step_time){
					for (uint8_t output_id=0; output_id<2; output_id++){
						if (light_var[j].led_level[output_id] > 0) 
							light_var[j].led_level[output_id] -= 1;
					}
					light_var[j].next_step_time += 1;
					light_var[j].step_time = millis();  	
				}
				
				bool end_cycling = true;
				for (uint8_t output_id=0; output_id<2; output_id++){
					end_cycling &= light_var[j].led_level[output_id] <= 0 ;
				}
				if (end_cycling){
					light_var[j].cycling = 0;
				}
				
			}
			//hold steady
			else if (cycle_time > 3000){
				
			}
			// ramping up
			else{
				volatile uint32_t ramping_time = curr_time - light_var[j].step_time;
				
				if (ramping_time > light_var[j].next_step_time){
					
					if (light_var[j].led_level[0] < light_max_level) 
						light_var[j].led_level[0] += 1;
					if (cycle_time > 1000){
						if (light_var[j].led_level[1] < light_max_level) 
						light_var[j].led_level[1] += 1;
					}
					light_var[j].next_step_time += 1;
					light_var[j].step_time = millis();  	
				}
			
			}				
		}
	}
	
	//>>>> Cricket <<<<<
	for (uint8_t j=0; j<WashingtonCricketNode::NUM_CRICKET; j++){
		
		for (uint8_t output_id=0; output_id<4; output_id++){
			cricket[j].set_output_level(output_id, cricket_var[j].output_level[output_id]);
		}

	}

	//>>>> Light <<<<<

	for (uint8_t j=0; j<WashingtonCricketNode::NUM_LIGHT; j++){
		
		for (uint8_t output_id=0; output_id<4; output_id++){
			light[j].set_output_level(output_id, light_var[j].led_level[output_id]);
		}

	}		

	
	//>> Print to Serial<<
	
	// crickets
	for (uint8_t j=0; j<WashingtonCricketNode::NUM_CRICKET; j++){
		
		// Device name
		Serial.print("== Cricket ");
		Serial.print(j);
		Serial.println(" ==");
		// IR sensor
		Serial.print("IR: (");
		Serial.print(cricket_var[j].ir_state);
		Serial.println(")");
		// Outputs
		Serial.print("Motor: (");
		for (uint8_t i=0; i<4; i++){
			Serial.print(cricket_var[j].output_level[i]);
			if (i<3){
				Serial.print(", ");
			}
		}
		Serial.println(")");

	}
	
	// Light
	for (uint8_t j=0; j<WashingtonCricketNode::NUM_LIGHT; j++){
		
		// Device name
		Serial.print("== Light ");
		Serial.print(j);
		Serial.println(" ==");
		// IR sensor
		Serial.print("IR: (");
		for (uint8_t i=0; i<2; i++){
			Serial.print(light_var[j].ir_state[i]);
			if (i<1){
				Serial.print(", ");
			}
		}
		Serial.println(")");
		// Outputs
		Serial.print("LED: (");
		for (uint8_t i=0; i<4; i++){
			Serial.print(light_var[j].led_level[i]);
			if (i<3){
				Serial.print(", ");
			}
		}
		Serial.println(")");

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
void WashingtonCricketNode::low_level_control_behaviour(const uint32_t &curr_time){

	
	//>>>> Cricket <<<<<

	for (uint8_t j=0; j<WashingtonCricketNode::NUM_CRICKET; j++){
		
		for (uint8_t output_id=0; output_id<4; output_id++){
			cricket[j].set_output_level(output_id, cricket_var[j].output_level[output_id]);
		}

	}

	//>>>> Light <<<<<

	for (uint8_t j=0; j<WashingtonCricketNode::NUM_LIGHT; j++){
		
		for (uint8_t output_id=0; output_id<4; output_id++){
			light[j].set_output_level(output_id, light_var[j].led_level[output_id]);
		}

	}		
}



//===========================================================================
//===== Washington Fin Cricket Node =====
//===========================================================================

WashingtonFinCricketNode::WashingtonFinCricketNode(uint8_t fin0_port_id, 
												   uint8_t fin1_port_id, 
												   uint8_t fin2_port_id,
												   uint8_t cricket0_port_id, 
												   uint8_t cricket1_port_id, 
												   uint8_t cricket2_port_id
											       ):
	FinsCricketsUnit(fin0_port_id, fin1_port_id, fin2_port_id, 
					 cricket0_port_id, cricket1_port_id, cricket2_port_id)
{
	//Serial.println("This is a WashingtonFin-Cricket Node");
}

WashingtonFinCricketNode::~WashingtonFinCricketNode(){
	
}

void WashingtonFinCricketNode::parse_msg(){

	
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
			// >>>>> byte 2 to byte 9: Fin 0
			// >>>>> byte 10 to byte 17: Fin 1
			// >>>>> byte 18 to byte 25: Fin 2			
			
			
			for (uint8_t j = 0; j < WashingtonFinCricketNode::NUM_FIN; j++){
				
				const uint8_t byte_offset = 8*(j) + device_offset;
						
				// byte x0 --- fin SMA wire 0
				fin_var[j].sma_level[0] = recv_data_buff[byte_offset+0];
				// byte x1 --- fin SMA wire 1
				fin_var[j].sma_level[1] = recv_data_buff[byte_offset+1];
				// byte x2 --- reflex actuation level
				fin_var[j].reflex_level[0] = recv_data_buff[byte_offset+2];
				// byte x3 --- reflex actuation level
				fin_var[j].reflex_level[1] = recv_data_buff[byte_offset+3];
			
			}
			
			device_offset += 8*WashingtonFinCricketNode::NUM_FIN;

			// (8 bytes each)
			// >>>>> byte 26 to byte 33: Cricket 0
			// >>>>> byte 34 to byte 41: Cricket 1
			// >>>>> byte 42 to byte 49: Cricket 2				
			
			for (uint8_t j = 0; j < WashingtonFinCricketNode::NUM_CRICKET; j++){
				
				const uint8_t byte_offset = 8*(j) + device_offset;
						
				// byte x0 --- actuator 0 level
				cricket_var[j].output_level[0] = recv_data_buff[byte_offset+0];
				// byte x1 --- actuator 1 level
				cricket_var[j].output_level[1] = recv_data_buff[byte_offset+1];
				// byte x2 --- actuator 2 level
				cricket_var[j].output_level[2] = recv_data_buff[byte_offset+2];
				// byte x3 --- actuator 3 level
				cricket_var[j].output_level[3] = recv_data_buff[byte_offset+3];
			
			}
		
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


//====== COMMUNICATION Protocol ======

void WashingtonFinCricketNode::compose_reply(byte front_signature, byte back_signature, byte msg_setting){


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
			
			// >>>>> byte 2 to byte 15: FIN 0
			// >>>>> byte 16 to byte 29: FIN 1
			// >>>>> byte 30 to byte 43: FIN 2
				
			for (uint8_t j = 0; j < WashingtonFinCricketNode::NUM_FIN; j++){
				
				const uint8_t byte_offset = 14*(j) + device_offset;
				
				// byte x0 --- IR 0 sensor state
				for (uint8_t i = 0; i < 2; i++)
					send_data_buff[byte_offset+0+i] = fin_var[j].ir_state[0] >> (8*i); 
				
				// byte x2 --- IR 1 sensor state
				for (uint8_t i = 0; i < 2; i++)
					send_data_buff[byte_offset+2+i] = fin_var[j].ir_state[1] >> (8*i); 
		
					
				// byte x4 -- Accelerometer state (x-axis)
				for (uint8_t i = 0; i < 2; i++)
					send_data_buff[byte_offset+4+i] = fin_var[j].acc_state[0] >> (8*i); 
			
				// byte x6 -- Accelerometer state (y-axis)
				for (uint8_t i = 0; i < 2; i++)
					send_data_buff[byte_offset+6+i] = fin_var[j].acc_state[1] >> (8*i); 
				
				// byte x8 -- Accelerometer state (z-axis)
				for (uint8_t i = 0; i < 2; i++)
					send_data_buff[byte_offset+8+i] = fin_var[j].acc_state[2] >> (8*i); 
				
				// byte x10 -- cycling
				send_data_buff[byte_offset+10] = (uint8_t) fin_var[j].cycling;
	
			}
			
			device_offset = 14*WashingtonFinCricketNode::NUM_FIN + device_offset;
			
			// (4 bytes each)
			// >>>>> byte 44 to byte 47: Cricket 0
			// >>>>> byte 48 to byte 51: Cricket 1
			// >>>>> byte 52 to byte 55: Cricket 2		
				
			for (uint8_t j = 0; j < WashingtonFinCricketNode::NUM_CRICKET; j++){
				
				const uint8_t byte_offset = 4*(j) + device_offset;
				
				// byte x0 --- IR 0 sensor state
				for (uint8_t i = 0; i < 2; i++)
					send_data_buff[byte_offset+0+i] = cricket_var[j].ir_state >> (8*i); 
				
	
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

//====== Input functions ======

//--- Sampling function ---
void WashingtonFinCricketNode::sample_inputs(){

	sample_inputs(0);
}

void WashingtonFinCricketNode::sample_inputs(const uint8_t setting){
	
	
	//=== Fin ===
			
	for (uint8_t j=0; j<WashingtonFinCricketNode::NUM_FIN; j++){
	
		//~~IR sensors state~~
		for (uint8_t i=0; i<2; i++){
		
			noInterrupts();
			fin_var[j].ir_state[i] = fin[j].read_analog_state(i);
			interrupts();
			
		}
		
		//~~Accelerometer~~		
		noInterrupts();
		fin[j].read_acc_state(fin_var[j].acc_state[0], 
							  fin_var[j].acc_state[1], 
							  fin_var[j].acc_state[2]);	
								   
		interrupts();
		
		
	}
	//=== Cricket ===
	for (uint8_t j=0; j<WashingtonFinCricketNode::NUM_CRICKET; j++){
	
		//~~IR sensors state~~
		noInterrupts();
		cricket_var[j].ir_state = cricket[j].read_analog_state(0);
		interrupts();
		
	}
	
}



//============ BEHAVIOUR CODES =========

//---- inactive behaviour ----
void WashingtonFinCricketNode::inactive_behaviour() {
	
	
	//=== Fin ===
	for (uint8_t i=0; i<WashingtonFinCricketNode::NUM_FIN; i++){

		fin[i].set_led_level(0, 0);
		fin[i].set_led_level(1, 0);
		
		fin[i].set_sma_level(0, 0);
		fin[i].set_sma_level(1, 0);
		
	}		
	
	//=== Cricket ===
	for (uint8_t i=0; i<WashingtonFinCricketNode::NUM_CRICKET; i++){
		
		for (uint8_t output_id=0; output_id<4; output_id++){
			cricket[i].set_output_level(output_id, 0);
		}

	}		
		
}

//---- test behaviour ----
void WashingtonFinCricketNode::test_behaviour(const uint32_t &curr_time) {
	
	//---- Fin cycling variables -----
	static uint32_t high_level_ctrl_fin_phase_time[WashingtonFinCricketNode::NUM_FIN] = {0, 0, 0};


	static uint8_t high_level_ctrl_sma0[WashingtonFinCricketNode::NUM_FIN] = {0, 0, 0};
	static uint8_t high_level_ctrl_sma1[WashingtonFinCricketNode::NUM_FIN] = {1, 1, 1};
	

	
	//~~~ fin cycle~~~~
	for (uint8_t j=0; j<WashingtonFinCricketNode::NUM_FIN; j++){
	

		
		if ((fin_var[j].ir_state[1] < 1200 && fin_var[j].ir_state[0] < 1200)
			&& fin_var[j].cycling < 1){
		
			fin[j].set_sma_level(0, 0);
			fin[j].set_sma_level(1, 0);
			fin_var[j].cycling  = 0;
			fin_var[j].motion_on = 3;
			continue;
		}
		
		// starting a cycle
		if (fin_var[j].cycling < 1){
			
			// behaviour Type
			switch (fin_var[j].motion_on){
				case 1:
					high_level_ctrl_sma0[j] = 0;
					high_level_ctrl_sma1[j] = 0;
				break;
				case 2:
					high_level_ctrl_sma0[j] = 1;
					high_level_ctrl_sma1[j] = 1;
				break;
				default:
					high_level_ctrl_sma0[j] = 0;
					high_level_ctrl_sma1[j] = 1;
				break;
			}
			fin_var[j].cycling = 1; //fin_var[j].motion_on;
			high_level_ctrl_fin_phase_time[j] = millis();  
			
			// turn on the first sma
			fin[j].set_sma_level(high_level_ctrl_sma0[j], fin_var[j].sma_max_level[0]);	
			fin[j].set_sma_level(high_level_ctrl_sma1[j],  fin_var[j].sma_max_level[1]);				
		}
		else{
			
			volatile uint32_t cycle_time = curr_time - high_level_ctrl_fin_phase_time[j];
			
			// if reaches the full period, restart cycle
			if (cycle_time > ((fin_var[j].arm_cycle_period[1] + fin_var[j].arm_cycle_period[0]) *100)){
				fin_var[j].cycling  = 0;
				fin_var[j].motion_on = 0;
			}
			
			//if reaches the on period 
			else if (cycle_time > (fin_var[j].arm_cycle_period[0]*100)){
				fin[j].set_sma_level(high_level_ctrl_sma1[j], 0);
				fin[j].set_sma_level(high_level_ctrl_sma0[j], 0);
			}		
		}
	}

	//>>>> Fin <<<<<

	for (uint8_t j=0; j<WashingtonFinCricketNode::NUM_FIN; j++){
		if (fin_var[j].ir_state[0] > 1200){
			fin[j].set_led_level(0, 250);
			fin[j].set_led_level(1, 250);
			// fin[j].set_sma_level(0, 250);
			// fin[j].set_sma_level(1, 250);
		}
		else{
			fin[j].set_led_level(0, 0);
			fin[j].set_led_level(1, 0);
			// fin[j].set_sma_level(0, 0);
			// fin[j].set_sma_level(1, 0);
		}
		
	}		
	
	//>>>> Cricket <<<<<

	for (uint8_t j=0; j<WashingtonFinCricketNode::NUM_CRICKET; j++){
		if (cricket_var[j].ir_state > 1200){
			for (uint8_t output_id=0; output_id<4; output_id++){
				cricket[j].set_output_level(output_id, 100);
			}
		}
		else{
			for (uint8_t output_id=0; output_id<4; output_id++){
				cricket[j].set_output_level(output_id, 0);
			}
			
		}

	}	
	
}

//---- self_running_behaviour ----
void WashingtonFinCricketNode::self_running_behaviour(const uint32_t &curr_time) {
	
	
	//---- Fin cycling variables -----
	static uint32_t high_level_ctrl_fin_phase_time[WashingtonFinCricketNode::NUM_FIN] = {0, 0, 0};


	static uint8_t high_level_ctrl_sma0[WashingtonFinCricketNode::NUM_FIN] = {0, 0, 0};
	static uint8_t high_level_ctrl_sma1[WashingtonFinCricketNode::NUM_FIN] = {1, 1, 1};
	
	

	
	//~~~ fin cycle~~~~
	for (uint8_t j=0; j<WashingtonFinCricketNode::NUM_FIN; j++){
	

		if ((fin_var[j].ir_state[1] < 1200 && fin_var[j].ir_state[0] < 1200)
			&& fin_var[j].cycling < 1){
		
			fin[j].set_sma_level(0, 0);
			fin[j].set_sma_level(1, 0);
			fin_var[j].cycling  = 0;
			fin_var[j].motion_on = 3;
			continue;
		}
		
		// starting a cycle
		if (fin_var[j].cycling < 1){
			
			// behaviour Type
			switch (fin_var[j].motion_on){
				case 1:
					high_level_ctrl_sma0[j] = 0;
					high_level_ctrl_sma1[j] = 0;
				break;
				case 2:
					high_level_ctrl_sma0[j] = 1;
					high_level_ctrl_sma1[j] = 1;
				break;
				default:
					high_level_ctrl_sma0[j] = 0;
					high_level_ctrl_sma1[j] = 1;
				break;
			}
			fin_var[j].cycling = 1; //fin_var[j].motion_on;
			high_level_ctrl_fin_phase_time[j] = millis();  
			
			// turn on the first sma
			fin[j].set_sma_level(high_level_ctrl_sma0[j], fin_var[j].sma_max_level[0]);	
			fin[j].set_sma_level(high_level_ctrl_sma1[j],  fin_var[j].sma_max_level[1]);				
		}
		else{
			
			volatile uint32_t cycle_time = curr_time - high_level_ctrl_fin_phase_time[j];
			
			// if reaches the full period, restart cycle
			if (cycle_time > ((fin_var[j].arm_cycle_period[1] + fin_var[j].arm_cycle_period[0]) *100)){
				fin_var[j].cycling  = 0;
				fin_var[j].motion_on = 0;
			}
			
			//if reaches the on period 
			else if (cycle_time > (fin_var[j].arm_cycle_period[0]*100)){
				fin[j].set_sma_level(high_level_ctrl_sma1[j], 0);
				fin[j].set_sma_level(high_level_ctrl_sma0[j], 0);
			}		
		}
	}


	//>>>> Fin Light <<<<<
	static uint8_t motor_max_level = 150;

	static uint8_t light_max_level = 255;
	for (uint8_t j=0; j<WashingtonFinCricketNode::NUM_FIN; j++){
		
		// starting a cycle
		if (fin_var[j].ir_state[0] > 1200 
			&& !fin_var[j].reflex_cycling){
			Serial.println("starting cycle");
			fin_var[j].reflex_cycling = true; 
			fin_var[j].reflex_phase_time = millis();  	
			fin_var[j].reflex_step_time = millis();
			fin_var[j].reflex_next_step_time = 2;
		}
		else if (fin_var[j].reflex_cycling) {
						
			volatile uint32_t cycle_time = curr_time - fin_var[j].reflex_phase_time;

			//ramping down
			// if reaches the full period, restart cycle
			if (cycle_time > 1500){
				
				volatile uint32_t ramping_time = curr_time - fin_var[j].reflex_step_time;
				
				if (ramping_time > fin_var[j].reflex_next_step_time){
					for (uint8_t output_id=0; output_id<2; output_id++){
						if (fin_var[j].reflex_level[output_id] > 0) 
							fin_var[j].reflex_level[output_id] -= 1;
					}
					fin_var[j].reflex_next_step_time += 1;
					fin_var[j].reflex_step_time = millis();  	
				}
				
				bool end_cycling = true;
				for (uint8_t output_id=0; output_id<2; output_id++){
					end_cycling &= fin_var[j].reflex_level[output_id] <= 0 ;
				}
				if (end_cycling){
					fin_var[j].reflex_cycling = 0;
				}
				
			}
			//hold steady
			else if (cycle_time > 1000){
				
			}
			// ramping up
			else{
				volatile uint32_t ramping_time = curr_time - fin_var[j].reflex_step_time;
				
				if (ramping_time > fin_var[j].reflex_next_step_time){
					
					if (fin_var[j].reflex_level[0] < light_max_level) 
						fin_var[j].reflex_level[0] += 1;
					if (fin_var[j].reflex_level[1] < motor_max_level) 
						fin_var[j].reflex_level[1] += 1;
					
					fin_var[j].reflex_next_step_time += 1;
					fin_var[j].reflex_step_time = millis();  	
				}
			
			}				
		}
	}
	
	for (uint8_t j=0; j<WashingtonFinCricketNode::NUM_FIN; j++){
			fin[j].set_led_level(0, fin_var[j].reflex_level[0]);
			fin[j].set_led_level(1, fin_var[j].reflex_level[1]);		
	}		
	
	static const uint16_t cricket_max_level = 150;

	//>>>> Cricket <<<<<
	for (uint8_t j=0; j<WashingtonFinCricketNode::NUM_CRICKET; j++){
		
		// starting a cycle
		if (cricket_var[j].ir_state > 1200 && !cricket_var[j].cycling){
			Serial.println("starting cycle");
			cricket_var[j].cycling = true; 
			cricket_var[j].phase_time = millis();  	
			cricket_var[j].step_time = millis();
			cricket_var[j].next_step_time = 1;
		}
		else if (cricket_var[j].cycling) {
						
			volatile uint32_t cycle_time = curr_time - cricket_var[j].phase_time;

			//ramping down
			// if reaches the full period, restart cycle
			if (cycle_time > 4000){
				
				volatile uint32_t ramping_time = curr_time - cricket_var[j].step_time;
				
				if (ramping_time > cricket_var[j].next_step_time){
					for (uint8_t output_id=0; output_id<4; output_id++){
						if (cricket_var[j].output_level[output_id] > 0) 
							cricket_var[j].output_level[output_id] -= 1;
					}
					cricket_var[j].next_step_time += 1;
					cricket_var[j].step_time = millis();  	
				}
				
				bool end_cycling = true;
				for (uint8_t output_id=0; output_id<4; output_id++){
					end_cycling &= cricket_var[j].output_level[output_id] <= 0 ;
				}
				if (end_cycling){
					cricket_var[j].cycling = 0;
				}
				
			}
			//hold steady
			else if (cycle_time > 3000){
				
			}
			// ramping up
			else{
				volatile uint32_t ramping_time = curr_time - cricket_var[j].step_time;
				
				if (ramping_time > cricket_var[j].next_step_time){
					for (uint8_t output_id=0; output_id<4; output_id++){
						if (cricket_var[j].output_level[output_id] < cricket_max_level) 
							cricket_var[j].output_level[output_id] += 1;
					}
					if (cricket_var[j].output_level[0] < cricket_max_level) 
							cricket_var[j].output_level[0] += 1;
		
					if (cycle_time > 500){
						if (cricket_var[j].output_level[1] < cricket_max_level) 
							cricket_var[j].output_level[1] += 1;
					}
					if (cycle_time > 1000){
						if (cricket_var[j].output_level[2] < cricket_max_level) 
							cricket_var[j].output_level[2] += 1;
					}
					if (cycle_time > 1500){
						if (cricket_var[j].output_level[3] < cricket_max_level) 
							cricket_var[j].output_level[3] += 1;
					}
					cricket_var[j].next_step_time += 1;
					cricket_var[j].step_time = millis();  	
				}
			
			}				
		}
	}

	
	//>>>> Cricket <<<<<
	for (uint8_t j=0; j<WashingtonCricketNode::NUM_CRICKET; j++){

		for (uint8_t output_id=0; output_id<4; output_id++){
			// Serial.print("c");
			// Serial.print(j);
			// Serial.print(".motor");
			// Serial.print(output_id);
			// Serial.print(": ");
			// Serial.println(cricket_var[j].output_level[output_id]);
			cricket[j].set_output_level(output_id, cricket_var[j].output_level[output_id]);
		}
	}
	
	

	
}

//---- indicator LED -----

void WashingtonFinCricketNode::led_blink_behaviour(const uint32_t &curr_time) {

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
void WashingtonFinCricketNode::low_level_control_behaviour(const uint32_t &curr_time){

	//>>>> FIN <<<<<
	for (uint8_t j=0; j<WashingtonFinCricketNode::NUM_FIN;j++){
		
				
		//sma protection mechanism
		if (fin_var[j].sma_level[0] > fin_var[j].sma_max_level[0])
			fin_var[j].sma_level[0] =  fin_var[j].sma_max_level[0];
		if (fin_var[j].sma_level[1] > fin_var[j].sma_max_level[1])
			fin_var[j].sma_level[1] =  fin_var[j].sma_max_level[1];
		
		fin[j].set_sma_level(0, fin_var[j].sma_level[0]);
		fin[j].set_sma_level(1, fin_var[j].sma_level[1]);
		fin[j].set_led_level(0, fin_var[j].reflex_level[0]);
		fin[j].set_led_level(1, fin_var[j].reflex_level[1]);

	
	}
	

	//>>>> Cricket <<<<<

	for (uint8_t j=0; j<WashingtonFinCricketNode::NUM_CRICKET; j++){
		
		for (uint8_t output_id=0; output_id<4; output_id++){
			cricket[j].set_output_level(output_id, cricket_var[j].output_level[output_id]);
		}

	}
}


//===========================================================================
//===== Washington Fin Node =====
//===========================================================================

WashingtonFinNode::WashingtonFinNode(uint8_t fin0_port_id, 
								   uint8_t fin1_port_id, 
								   uint8_t fin2_port_id,
								   uint8_t light0_port_id, 
								   uint8_t light1_port_id, 
								   uint8_t light2_port_id
								   ):
	FinsLightsUnit(fin0_port_id, fin1_port_id, fin2_port_id, 
					 light0_port_id, light1_port_id, light2_port_id)
{
	//Serial.println("This is a Washington Fin Node");
}

WashingtonFinNode::~WashingtonFinNode(){
	
}

void WashingtonFinNode::parse_msg(){

	
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
		
		//low level requests
		case 2: {
		
			uint8_t  device_offset = 2;

			// (8 bytes each)
			// >>>>> byte 2 to byte 9: Fin 0
			// >>>>> byte 10 to byte 17: Fin 1
			// >>>>> byte 18 to byte 25: Fin 2			
			
			
			for (uint8_t j = 0; j < WashingtonFinNode::NUM_FIN; j++){
				
				const uint8_t byte_offset = 8*(j) + device_offset;
						
				// byte x0 --- fin SMA wire 0
				fin_var[j].sma_level[0] = recv_data_buff[byte_offset+0];
				// byte x1 --- fin SMA wire 1
				fin_var[j].sma_level[1] = recv_data_buff[byte_offset+1];
				// byte x2 --- reflex actuation level
				fin_var[j].reflex_level[0] = recv_data_buff[byte_offset+2];
				// byte x3 --- reflex actuation level
				fin_var[j].reflex_level[1] = recv_data_buff[byte_offset+3];
			
			}
			
			device_offset += 8*WashingtonFinNode::NUM_FIN;

			// (8 bytes each)
			// >>>>> byte 26 to byte 33: Light 0
			// >>>>> byte 34 to byte 41: Light 1
			// >>>>> byte 42 to byte 49: Light 2				
			
			for (uint8_t j = 0; j < WashingtonFinNode::NUM_LIGHT; j++){
				
				const uint8_t byte_offset = 8*(j) + device_offset;
						
				// byte x0 --- LED 0 level
				light_var[j].led_level[0] = recv_data_buff[byte_offset+0];
				// byte x1 --- LED 1 level
				light_var[j].led_level[1] = recv_data_buff[byte_offset+1];
				// byte x2 --- LED 2 level
				light_var[j].led_level[2] = recv_data_buff[byte_offset+2];
				// byte x3 --- LED 3 level
				light_var[j].led_level[3] = recv_data_buff[byte_offset+3];
			
			}
		
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


//====== COMMUNICATION Protocol ======

void WashingtonFinNode::compose_reply(byte front_signature, byte back_signature, byte msg_setting){


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
			
			// >>>>> byte 2 to byte 15: FIN 0
			// >>>>> byte 16 to byte 29: FIN 1
			// >>>>> byte 30 to byte 43: FIN 2
				
			for (uint8_t j = 0; j < WashingtonFinNode::NUM_FIN; j++){
				
				const uint8_t byte_offset = 14*(j) + device_offset;
				
				// byte x0 --- IR 0 sensor state
				for (uint8_t i = 0; i < 2; i++)
					send_data_buff[byte_offset+0+i] = fin_var[j].ir_state[0] >> (8*i); 
				
				// byte x2 --- IR 1 sensor state
				for (uint8_t i = 0; i < 2; i++)
					send_data_buff[byte_offset+2+i] = fin_var[j].ir_state[1] >> (8*i); 
		
					
				// byte x4 -- Accelerometer state (x-axis)
				for (uint8_t i = 0; i < 2; i++)
					send_data_buff[byte_offset+4+i] = fin_var[j].acc_state[0] >> (8*i); 
			
				// byte x6 -- Accelerometer state (y-axis)
				for (uint8_t i = 0; i < 2; i++)
					send_data_buff[byte_offset+6+i] = fin_var[j].acc_state[1] >> (8*i); 
				
				// byte x8 -- Accelerometer state (z-axis)
				for (uint8_t i = 0; i < 2; i++)
					send_data_buff[byte_offset+8+i] = fin_var[j].acc_state[2] >> (8*i); 
				
				// byte x10 -- cycling
				send_data_buff[byte_offset+10] = (uint8_t) fin_var[j].cycling;
	
			}
			
			device_offset = 14*WashingtonFinNode::NUM_FIN + device_offset;
			
			// (4 bytes each)
			// >>>>> byte 44 to byte 47: LIGHT 0
			// >>>>> byte 48 to byte 51: LIGHT 1
			// >>>>> byte 52 to byte 55: LIGHT 2		
				
			for (uint8_t j = 0; j < WashingtonFinNode::NUM_LIGHT; j++){
				
				const uint8_t byte_offset = 4*(j) + device_offset;
				
				// byte x0 --- IR 0 sensor state
				for (uint8_t i = 0; i < 2; i++)
					send_data_buff[byte_offset+0+i] = light_var[j].ir_state[0] >> (8*i); 
				// byte x2 --- IR 1 sensor state
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

//====== Input functions ======

//--- Sampling function ---
void WashingtonFinNode::sample_inputs(){

	sample_inputs(0);
}

void WashingtonFinNode::sample_inputs(const uint8_t setting){
	
	
	//=== Fin ===
			
	for (uint8_t j=0; j<WashingtonFinNode::NUM_FIN; j++){
	
		//~~IR sensors state~~
		for (uint8_t i=0; i<2; i++){
		
			noInterrupts();
			fin_var[j].ir_state[i] = fin[j].read_analog_state(i);
			interrupts();
			
		}
		
		//~~Accelerometer~~		
		noInterrupts();
		fin[j].read_acc_state(fin_var[j].acc_state[0], 
							  fin_var[j].acc_state[1], 
							  fin_var[j].acc_state[2]);	
								   
		interrupts();
		
		
	}
	//=== LIGHT ===
	
	for (uint8_t j=0; j<WashingtonFinNode::NUM_LIGHT; j++){
	
		//~~IR sensors state~~
		for (uint8_t i=0; i<2; i++){
		
			noInterrupts();
			light_var[j].ir_state[i] = light[j].read_analog_state(i);
			interrupts();
			
		}
		
	}
	
}


//============ BEHAVIOUR CODES =========

//---- inactive behaviour ----
void WashingtonFinNode::inactive_behaviour() {
	
	
	//=== Fin ===
	for (uint8_t i=0; i<WashingtonFinNode::NUM_FIN; i++){

		fin[i].set_led_level(0, 0);
		fin[i].set_led_level(1, 0);
		
		fin[i].set_sma_level(0, 0);
		fin[i].set_sma_level(1, 0);
		
	}		
	
	//=== Cricket ===
	for (uint8_t i=0; i<WashingtonFinNode::NUM_LIGHT; i++){
		
		for (uint8_t output_id=0; output_id<4; output_id++){
			light[i].set_output_level(output_id, 0);
		}

	}		
		
}

//---- test behaviour ----
void WashingtonFinNode::test_behaviour(const uint32_t &curr_time) {
	
	//---- Fin cycling variables -----
	static uint32_t high_level_ctrl_fin_phase_time[WashingtonFinNode::NUM_FIN] = {0, 0, 0};


	static uint8_t high_level_ctrl_sma0[WashingtonFinNode::NUM_FIN] = {0, 0, 0};
	static uint8_t high_level_ctrl_sma1[WashingtonFinNode::NUM_FIN] = {1, 1, 1};
	

	
	//~~~ fin cycle~~~~
	for (uint8_t j=0; j<WashingtonFinNode::NUM_FIN; j++){
	

		
		if (fin_var[j].motion_on < 1 && fin_var[j].cycling < 1){
		
			fin[j].set_sma_level(0, 0);
			fin[j].set_sma_level(1, 0);
			fin_var[j].cycling  = 0;
			fin_var[j].motion_on = 3;
			continue;
		}
		
			
		// starting a cycle
		if (fin_var[j].cycling < 1){
			
			// behaviour Type
			switch (fin_var[j].motion_on){
				case 1:
					high_level_ctrl_sma0[j] = 0;
					high_level_ctrl_sma1[j] = 0;
				break;
				case 2:
					high_level_ctrl_sma0[j] = 1;
					high_level_ctrl_sma1[j] = 1;
				break;
				default:
					high_level_ctrl_sma0[j] = 0;
					high_level_ctrl_sma1[j] = 1;
				break;
			}
			fin_var[j].cycling = 1; //fin_var[j].motion_on;
			high_level_ctrl_fin_phase_time[j] = millis();  
			
			// turn on the first sma
			fin[j].set_sma_level(high_level_ctrl_sma0[j], fin_var[j].sma_max_level[0]);	
			fin[j].set_sma_level(high_level_ctrl_sma1[j],  fin_var[j].sma_max_level[1]);				
		}
		else{
			
			
			volatile uint32_t cycle_time = curr_time - high_level_ctrl_fin_phase_time[j];
			
			// if reaches the full period, restart cycle
			if (cycle_time > ((fin_var[j].arm_cycle_period[1] + fin_var[j].arm_cycle_period[0]) *100)){
				fin_var[j].cycling  = 0;
				fin_var[j].motion_on = 0;
			}
			
			//if reaches the on period 
			else if (cycle_time > (fin_var[j].arm_cycle_period[0]*100)){
				fin[j].set_sma_level(high_level_ctrl_sma1[j], 0);
				fin[j].set_sma_level(high_level_ctrl_sma0[j], 0);

			}
				
		}
		

	}

	

	
	//>>>> Fin <<<<<
	
	for (uint8_t j=0; j<WashingtonFinNode::NUM_FIN; j++){
		if (fin_var[j].ir_state[0] > 1200){
			fin[j].set_led_level(0, 250);
			fin[j].set_led_level(1, 250);
			// fin[j].set_sma_level(0, 250);
			// fin[j].set_sma_level(1, 250);
		}
		else{
			fin[j].set_led_level(0, 0);
			fin[j].set_led_level(1, 0);
			// fin[j].set_sma_level(0, 0);
			// fin[j].set_sma_level(1, 0);
		}
	}		
	
	//>>>> Light <<<<<

	for (uint8_t j=0; j<WashingtonFinNode::NUM_LIGHT; j++){
		if (light_var[j].ir_state[0] > 1200){
			for (uint8_t output_id=0; output_id<4; output_id++){
				light[j].set_output_level(output_id, 255);
			}
		}
		else{
			for (uint8_t output_id=0; output_id<4; output_id++){
				light[j].set_output_level(output_id, 0);
			}
			
		}

	}	
	
}

//---- self_running_behaviour ----
void WashingtonFinNode::self_running_behaviour(const uint32_t &curr_time) {
	//---- Fin cycling variables -----
	static uint32_t high_level_ctrl_fin_phase_time[WashingtonFinNode::NUM_FIN] = {0, 0, 0};


	static uint8_t high_level_ctrl_sma0[WashingtonFinNode::NUM_FIN] = {0, 0, 0};
	static uint8_t high_level_ctrl_sma1[WashingtonFinNode::NUM_FIN] = {1, 1, 1};
	
	

	
	//~~~ fin cycle~~~~
	for (uint8_t j=0; j<WashingtonFinNode::NUM_FIN; j++){
	

		if ((fin_var[j].ir_state[1] < 1200 && fin_var[j].ir_state[0] < 1200)
			&& fin_var[j].cycling < 1){
		
			fin[j].set_sma_level(0, 0);
			fin[j].set_sma_level(1, 0);
			fin_var[j].cycling  = 0;
			fin_var[j].motion_on = 3;
			continue;
		}
		
		// starting a cycle
		if (fin_var[j].cycling < 1){
			
			// behaviour Type
			switch (fin_var[j].motion_on){
				case 1:
					high_level_ctrl_sma0[j] = 0;
					high_level_ctrl_sma1[j] = 0;
				break;
				case 2:
					high_level_ctrl_sma0[j] = 1;
					high_level_ctrl_sma1[j] = 1;
				break;
				default:
					high_level_ctrl_sma0[j] = 0;
					high_level_ctrl_sma1[j] = 1;
				break;
			}
			fin_var[j].cycling = 1; //fin_var[j].motion_on;
			high_level_ctrl_fin_phase_time[j] = millis();  
			
			// turn on the first sma
			fin[j].set_sma_level(high_level_ctrl_sma0[j], fin_var[j].sma_max_level[0]);	
			fin[j].set_sma_level(high_level_ctrl_sma1[j],  fin_var[j].sma_max_level[1]);				
		}
		else{
			
			volatile uint32_t cycle_time = curr_time - high_level_ctrl_fin_phase_time[j];
			
			// if reaches the full period, restart cycle
			if (cycle_time > ((fin_var[j].arm_cycle_period[1] + fin_var[j].arm_cycle_period[0]) *100)){
				fin_var[j].cycling  = 0;
				fin_var[j].motion_on = 0;
			}
			
			//if reaches the on period 
			else if (cycle_time > (fin_var[j].arm_cycle_period[0]*100)){
				fin[j].set_sma_level(high_level_ctrl_sma1[j], 0);
				fin[j].set_sma_level(high_level_ctrl_sma0[j], 0);
			}		
		}
	}


	//>>>> Fin Light <<<<<
	static uint8_t motor_max_level = 150;

	static uint8_t light_max_level = 255;
	for (uint8_t j=0; j<WashingtonFinNode::NUM_FIN; j++){
		
		// starting a cycle
		if (fin_var[j].ir_state[0] > 1200 
			&& !fin_var[j].reflex_cycling){
			Serial.println("starting cycle");
			fin_var[j].reflex_cycling = true; 
			fin_var[j].reflex_phase_time = millis();  	
			fin_var[j].reflex_step_time = millis();
			fin_var[j].reflex_next_step_time = 2;
		}
		else if (fin_var[j].reflex_cycling) {
						
			volatile uint32_t cycle_time = curr_time - fin_var[j].reflex_phase_time;

			//ramping down
			// if reaches the full period, restart cycle
			if (cycle_time > 1500){
				
				volatile uint32_t ramping_time = curr_time - fin_var[j].reflex_step_time;
				
				if (ramping_time > fin_var[j].reflex_next_step_time){
					for (uint8_t output_id=0; output_id<2; output_id++){
						if (fin_var[j].reflex_level[output_id] > 0) 
							fin_var[j].reflex_level[output_id] -= 1;
					}
					fin_var[j].reflex_next_step_time += 1;
					fin_var[j].reflex_step_time = millis();  	
				}
				
				bool end_cycling = true;
				for (uint8_t output_id=0; output_id<2; output_id++){
					end_cycling &= fin_var[j].reflex_level[output_id] <= 0 ;
				}
				if (end_cycling){
					fin_var[j].reflex_cycling = 0;
				}
				
			}
			//hold steady
			else if (cycle_time > 1000){
				
			}
			// ramping up
			else{
				volatile uint32_t ramping_time = curr_time - fin_var[j].reflex_step_time;
				
				if (ramping_time > fin_var[j].reflex_next_step_time){
					
					if (fin_var[j].reflex_level[0] < light_max_level) 
						fin_var[j].reflex_level[0] += 1;
					if (fin_var[j].reflex_level[1] < motor_max_level) 
						fin_var[j].reflex_level[1] += 1;
					
					fin_var[j].reflex_next_step_time += 1;
					fin_var[j].reflex_step_time = millis();  	
				}
			
			}				
		}
	}
	



	
}

//---- indicator LED -----

void WashingtonFinNode::led_blink_behaviour(const uint32_t &curr_time) {

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
void WashingtonFinNode::low_level_control_behaviour(const uint32_t &curr_time){
	

	//>>>> FIN <<<<<
	for (uint8_t j=0; j<WashingtonFinNode::NUM_FIN;j++){
		
				
		//sma protection mechanism
		if (fin_var[j].sma_level[0] > fin_var[j].sma_max_level[0])
			fin_var[j].sma_level[0] =  fin_var[j].sma_max_level[0];
		if (fin_var[j].sma_level[1] > fin_var[j].sma_max_level[1])
			fin_var[j].sma_level[1] =  fin_var[j].sma_max_level[1];
		
		fin[j].set_sma_level(0, fin_var[j].sma_level[0]);
		fin[j].set_sma_level(1, fin_var[j].sma_level[1]);
		fin[j].set_led_level(0, fin_var[j].reflex_level[0]);
		fin[j].set_led_level(1, fin_var[j].reflex_level[1]);

	
	}

	//>>>> Light <<<<<

	for (uint8_t j=0; j<WashingtonFinNode::NUM_LIGHT; j++){
		
		for (uint8_t output_id=0; output_id<4; output_id++){
			light[j].set_output_level(output_id, light_var[j].led_level[output_id]);
		}

	}
}




//===========================================================================
//===== Washington Sound Node =====
//===========================================================================

WashingtonSoundNode::WashingtonSoundNode(uint8_t sound0_port_id, 
										uint8_t sound1_port_id, 
										uint8_t sound2_port_id,
										uint8_t sound3_port_id, 
										uint8_t sound4_port_id, 
										uint8_t sound5_port_id
										):
			SoundsUnit(sound0_port_id, sound1_port_id, sound2_port_id, 
					   sound3_port_id, sound4_port_id, sound5_port_id)
{
	
}

WashingtonSoundNode::~WashingtonSoundNode(){
	
}

void WashingtonSoundNode::parse_msg(){

	
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
		
		//low level requests
		case 2: {
		
			uint8_t  device_offset = 2;

			// (8 bytes each)
			// >>>>> byte 2 to byte 9: Sound 0
			// >>>>> byte 10 to byte 17: Sound 1
			// >>>>> byte 18 to byte 25: Sound 2		
			// >>>>> byte 26 to byte 33: Sound 3
			// >>>>> byte 34 to byte 41: Sound 4
			// >>>>> byte 42 to byte 49: Sound 5				
			
			
			for (uint8_t j = 0; j < WashingtonSoundNode::NUM_SOUND; j++){
				
				const uint8_t byte_offset = 8*(j) + device_offset;
						
				// byte x0 --- sound PWM output 0
				sound_var[j].output_level[0] = recv_data_buff[byte_offset+0];
				// byte x1 --- sound PWM output 1
				sound_var[j].output_level[1] = recv_data_buff[byte_offset+1];
				
				// byte x2 --- sound type left
				sound_var[j].sound_type[0] = recv_data_buff[byte_offset+2];
				// byte x3 --- sound type right
				sound_var[j].sound_type[1] = recv_data_buff[byte_offset+3];
				
				// byte x4 --- sound volume left
				sound_var[j].sound_volume[0] = recv_data_buff[byte_offset+4];
				// byte x5 --- sound volume right
				sound_var[j].sound_volume[1] = recv_data_buff[byte_offset+5];
				
				// byte x6 --- sound block left
				sound_var[j].sound_block[0] = recv_data_buff[byte_offset+6];
				// byte x7 --- sound block right
				sound_var[j].sound_block[1] = recv_data_buff[byte_offset+7];
			}
	
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

void WashingtonSoundNode::compose_reply(byte front_signature, byte back_signature, byte msg_setting){


	// add the signatures to first and last byte
	send_data_buff[0] = front_signature;
	send_data_buff[num_outgoing_byte-1] = back_signature;
		
	if (msg_setting == 0){
		// sample the sensors
		this->sample_inputs();	
	}
	
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
			
			// >>>>> byte 2 to byte 9: Sound 0
			// >>>>> byte 10 to byte 17: Sound 1
			// >>>>> byte 18 to byte 25: Sound 2
			// >>>>> byte 26 to byte 33: Sound 3	
			// >>>>> byte 34 to byte 41: Sound 4
			// >>>>> byte 42 to byte 49: Sound 5				
			for (uint8_t j = 0; j < WashingtonSoundNode::NUM_SOUND; j++){
				
				const uint8_t byte_offset = 8*(j) + device_offset;
				
				// byte x0 --- IR 0 sensor state
				for (uint8_t i = 0; i < 2; i++)
					send_data_buff[byte_offset+0+i] = sound_var[j].analog_state[0] >> (8*i); 
				
				// byte x2 --- IR 1 sensor state
				for (uint8_t i = 0; i < 2; i++)
					send_data_buff[byte_offset+2+i] = sound_var[j].analog_state[1] >> (8*i); 
				
				// byte x4 --- IR 2 sensor state
				for (uint8_t i = 0; i < 2; i++)
					send_data_buff[byte_offset+4+i] = sound_var[j].analog_state[2] >> (8*i); 
		
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
void WashingtonSoundNode::sample_inputs(){

	sample_inputs(0);
}

void WashingtonSoundNode::sample_inputs(const uint8_t setting){
	
	
	//=== Sound ===
			
	for (uint8_t j=0; j<WashingtonSoundNode::NUM_SOUND; j++){

		//~~Analog inputs~~		
		// noInterrupts();
		sound[j].read_analog_state(sound_var[j].analog_state[0], 
								   sound_var[j].analog_state[1], 
								   sound_var[j].analog_state[2]);	
								   
		// interrupts();
		
		
	}

	
}



//===========================================================================
//============ BEHAVIOUR CODES =========
//===========================================================================

//---- inactive behaviour ----
void WashingtonSoundNode::inactive_behaviour() {
	
	
	//=== Sound ===
	for (uint8_t j=0; j<WashingtonSoundNode::NUM_SOUND; j++){
		
		for (uint8_t i=0; i<2; i++){
			sound[j].set_output_level(i, 0);
		}
		for (uint8_t i=0; i<2; i++){
			sound[j].set_digital_trigger(i, false);
		}

	}		
			
}

//---- test behaviour ----
void WashingtonSoundNode::test_behaviour(const uint32_t &curr_time) {
	
	static int song_id = 1;
	
	for (uint8_t j=0; j<WashingtonSoundNode::NUM_SOUND; j++){
		Serial.println(sound_var[j].analog_state[0]);
		if (sound_var[j].analog_state[0] > 1200){
			Serial.println(song_id);

			sound[j].set_output_level(0, 100);
			sound[j].play_sound(song_id,  10, 2, 0, true);
			song_id += 1;
			if (song_id > 4){
				song_id = 1;
			}

		}
		else{
			sound[j].set_output_level(0, 0);
			
		}
		
		if(sound_var[j].analog_state[1] > 1200){
			sound[j].set_output_level(1, 100);
			sound[j].play_sound(2, 10, 1, 0, true);
		}
		else{
			
			sound[j].set_output_level(1, 0);
			
		}
		
		
	}		
	
}

//---- self_running_behaviour ----
void WashingtonSoundNode::self_running_behaviour(const uint32_t &curr_time) {
	// low_level_control_behaviour(curr_time);
	test_behaviour(curr_time);
}

//---- indicator LED -----

void WashingtonSoundNode::led_blink_behaviour(const uint32_t &curr_time) {

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
void WashingtonSoundNode::low_level_control_behaviour(const uint32_t &curr_time){

	//>>>> PWM <<<<<
	for (uint8_t j=0; j<WashingtonSoundNode::NUM_SOUND;j++){
		
		sound[j].set_output_level(0, sound_var[j].output_level[0]);
		sound[j].set_output_level(1, sound_var[j].output_level[1]);
	}

	//>>>> Sound <<<<<
	for (uint8_t j=0; j<WashingtonSoundNode::NUM_SOUND; j++){
		
		for (uint8_t channel=0; channel<2; channel++){
			if (sound_var[j].sound_type[channel]){
				sound[j].play_sound(sound_var[j].sound_type[channel], 
									sound_var[j].sound_volume[channel], 
									channel, 0, 
									sound_var[j].sound_block[channel]>0);
			}
			
		}

	}

}


