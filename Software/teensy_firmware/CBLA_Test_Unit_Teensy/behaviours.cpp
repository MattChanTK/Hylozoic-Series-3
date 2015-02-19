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
		//Tentacles high level requests
		case 2: {
		
			// (14 bytes each)
			// >>>>> byte 2 to byte 15: TENTACLE 0
			// >>>>> byte 16 to byte 29: TENTACLE 1
			// >>>>> byte 30 to byte 43: TENTACLE 2	
			// >>>>> byte 44 to byte 57: TENTACLE 3			
			for (uint8_t j = 0; j < 4; j++){
						
				const uint8_t byte_offset = 14*(j) + 2;
			
				//--- internal variables---
				
				// byte x0 --- IR sensor 0 activation threshold
				temp_val = 0;
				for (uint8_t i = 0; i < wave_size; i++)
					temp_val += recv_data_buff[byte_offset+i+0] << (8*i);
				tentacle_var[j].tentacle_ir_threshold[0] = temp_val;
					
				// byte x2 --- IR sensor 1 activation threshold
				temp_val = 0;
				for (uint8_t i = 0; i < wave_size; i++)
					temp_val += recv_data_buff[byte_offset+i+2] << (8*i);
				tentacle_var[j].tentacle_ir_threshold[1] = temp_val;
					
				// byte x4 --- ON period of Tentacle arm activation
				tentacle_var[j].tentacle_arm_cycle_period[0] = recv_data_buff[byte_offset+4];
				
				// byte x5 --- OFF period of Tentacle arm activation
				tentacle_var[j].tentacle_arm_cycle_period[1] = recv_data_buff[byte_offset+5];
				
				// byte x6 --- Reflex channel 1 period 
				temp_val = 0;
				for (uint8_t i = 0; i < wave_size; i++)
					temp_val += recv_data_buff[byte_offset+i+6] << (8*i);
				tentacle_var[j].tentacle_reflex_period[0] = temp_val;
				
				// byte x8 --- Reflex channel 2 period 
				temp_val = 0;
				for (uint8_t i = 0; i < wave_size; i++)
					temp_val += recv_data_buff[byte_offset+i+8] << (8*i);
				tentacle_var[j].tentacle_reflex_period[1] = temp_val;
					
					
				//--- actuator output variables---
				
				// byte x10 --- tentacle motion activation 
				tentacle_var[j].tentacle_motion_on = recv_data_buff[byte_offset+10];
				
				// byte x11 --- reflex channel 1 wave type 
				tentacle_var[j].tentacle_reflex_wave_type[0] = recv_data_buff[byte_offset+11];
				
				// byte x12 --- reflex channel 2 wave type 
				tentacle_var[j].tentacle_reflex_wave_type[1] = recv_data_buff[byte_offset+12];
				

			}
			break;
		}
			
		// Tentacles low level requests
		case 3: {
		
			// (14 bytes each)
			// >>>>> byte 2 to byte 15: TENTACLE 0
			// >>>>> byte 16 to byte 29: TENTACLE 1
			// >>>>> byte 30 to byte 43: TENTACLE 2	
			// >>>>> byte 44 to byte 57: TENTACLE 3		
			
			for (uint8_t j = 0; j < 4; j++){
				
				const uint8_t byte_offset = 14*(j) + 2;
						
				// byte x0 --- tentacle SMA wire 0
				tentacle_var[j].tentacle_sma_level[0] = recv_data_buff[byte_offset+0];
				// byte x1 --- tentacle SMA wire 1
				tentacle_var[j].tentacle_sma_level[1] = recv_data_buff[byte_offset+1];
				// byte x2 --- reflex actuation level
				tentacle_var[j].tentacle_reflex_level[0] = recv_data_buff[byte_offset+2];
				// byte x4 --- reflex actuation level
				tentacle_var[j].tentacle_reflex_level[1] = recv_data_buff[byte_offset+3];
			
			}
			break;
		
		}
		
		// Protocell requests
		case 4: {
			
			// (15 bytes each)
			// >>>>> byte 2 to byte 16: PROTOCELL 0
			// >>>>> byte 17 to byte 31: PROTOCELL 1
			for (uint8_t j = 0; j < 2; j++){
						
				const uint8_t byte_offset = 15*(j) + 2;
				
				// --- internal variables ----
				// byte x0 --- Ambient light sensor threshold
				temp_val = 0;
				for (uint8_t i = 0; i < wave_size; i++)
					temp_val += recv_data_buff[byte_offset+i+0] << (8*i);
				tentacle_var[j].tentacle_reflex_period[1] = temp_val;
					
				// byte x2 --- high-power LED cycle period 
				temp_val = 0;
				for (uint8_t i = 0; i < wave_size; i++)
					temp_val += recv_data_buff[byte_offset+i+2] << (8*i);
				protocell_var[j].protocell_cycle_period = temp_val;
					
				//--- actuator output variables---
				// byte x4 --- high-power LED level 
				protocell_var[j].protocell_led_level = recv_data_buff[byte_offset+4];
				
				// byte x5 --- high-power led wave type 
				protocell_var[j].protocell_led_wave_type = recv_data_buff[byte_offset+5];
						
			}
			break;
		
		}
		
		// wave forms
		case 10: {
		
			//byte 2 wave type to change
			uint8_t wave_type = recv_data_buff[2];
			
			if (wave_type < num_wave){
				
				// byte 12 to 43 --- indicator LED wave 
				for (uint8_t i = 0; i < wave_size; i++)
					wave[wave_type].waveform[i] = recv_data_buff[i+12];
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

void Behaviours::compose_reply(byte front_signature, byte back_signature, byte msg_setting){


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
		
			// >>>>> byte 2 to byte 9: Protocell 0 and 1
		
			// byte 2 --- ambient light sensor 0 state
			for (uint8_t i = 0; i < 2; i++)
				send_data_buff[2+i] = protocell_var[0].protocell_als_state >> (8*i); 
				
			// byte 4 --- ambient light sensor 1 state
			for (uint8_t i = 0; i < 2; i++)
				send_data_buff[4+i] = protocell_var[1].protocell_als_state >> (8*i);
				
				
			// >>>>> byte 10 to byte 19: TENTACLE 0
			// >>>>> byte 20 to byte 29: TENTACLE 1
			// >>>>> byte 30 to byte 39: TENTACLE 2		
			// >>>>> byte 40 to byte 49: TENTACLE 3
				
			for (uint8_t j = 0; j < 4; j++){
				
				const uint8_t byte_offset = 10*(j) + 10;
				
				// byte x0 --- IR 0 sensor state
				for (uint8_t i = 0; i < 2; i++)
					send_data_buff[byte_offset+0+i] = tentacle_var[j].tentacle_ir_state[0] >> (8*i); 
				
				// byte x2 --- IR 1 sensor state
				for (uint8_t i = 0; i < 2; i++)
					send_data_buff[byte_offset+2+i] = tentacle_var[j].tentacle_ir_state[1] >> (8*i); 
		
					
				// byte x4 -- Accelerometer state (x-axis)
				for (uint8_t i = 0; i < 2; i++)
					send_data_buff[byte_offset+4+i] = tentacle_var[j].tentacle_acc_state[0] >> (8*i); 
			
				// byte x6 -- Accelerometer state (y-axis)
				for (uint8_t i = 0; i < 2; i++)
					send_data_buff[byte_offset+6+i] = tentacle_var[j].tentacle_acc_state[1] >> (8*i); 
				
				// byte x8 -- Accelerometer state (z-axis)
				for (uint8_t i = 0; i < 2; i++)
					send_data_buff[byte_offset+8+i] = tentacle_var[j].tentacle_acc_state[2] >> (8*i); 
	
			}
			
			// >>>>> byte 50: TENTACLE 0
			// >>>>> byte 51: TENTACLE 1
			// >>>>> byte 52: TENTACLE 2		
			// >>>>> byte 53: TENTACLE 3
			for (uint8_t j = 0; j < 4; j++){
			
				const uint8_t byte_offset = 50+(j);
				
				send_data_buff[byte_offset] = (uint8_t) tentacle_var[j].tentacle_cycling;
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
void Behaviours::sample_inputs(){

	sample_inputs(0);
}

void Behaviours::sample_inputs(const uint8_t setting){

	const uint8_t read_buff_num = 1;
	
	//>>>Tentacle<<<
			
	for (uint8_t j=0; j<4; j++){
	
		//~~IR sensors state~~
		for (uint8_t i=0; i<2; i++){
		
			uint32_t read_buff = 0;
			for (uint8_t k=0; k<read_buff_num; k++){
				read_buff += tentacle[j].read_analog_state(i);
			}
			noInterrupts()
			tentacle_var[j].tentacle_ir_state[i] = (uint16_t) (read_buff/read_buff_num);
			interrupts()
		}
	
		
		//~~Accelerometer~~		
		noInterrupts();
		tentacle[j].read_acc_state(tentacle_var[j].tentacle_acc_state[0], 
								   tentacle_var[j].tentacle_acc_state[1], 
								   tentacle_var[j].tentacle_acc_state[2]);	
								   
		interrupts();
		
		
	}
	
	if (Wire.frozen){
		//digitalWrite(PGM_DO_pin, 1);
		digitalWrite(13, 1);
	}
		
	
	
	//>>>Protocell<<<

	for (uint8_t j = 0; j<2; j++){
	
		//~~Ambient Light Sensor~~
		uint32_t read_buff = 0;
		for (uint8_t k=0; k<read_buff_num; k++){
			read_buff += protocell[j].read_analog_state();
		}
		noInterrupts();
		protocell_var[j].protocell_als_state = (uint16_t) (read_buff/read_buff_num);
		interrupts();
	}


}



//===========================================================================
//============ BEHAVIOUR CODES =========
//===========================================================================


//---- test behaviour ----
void Behaviours::test_behaviour(const uint32_t &curr_time) {
	
	//=== testing Tentacle ===
	for (uint8_t i=0; i<3; i++){
		uint16_t ir_range = tentacle[i].read_analog_state(0);
		if (ir_range > 1200){
			tentacle[i].set_led_level(0, 250);
			tentacle[i].set_led_level(1, 250);
		}
		else{
			tentacle[i].set_led_level(0, 0);
			tentacle[i].set_led_level(1, 0);
		}
		
		ir_range = tentacle[i].read_analog_state(1);
		
		if (ir_range < 00){
			tentacle[i].set_sma_level(0, 250);
			tentacle[i].set_sma_level(1, 250);
			
		}
		else{
			tentacle[i].set_sma_level(0, 0);
			tentacle[i].set_sma_level(1, 0);
		}
	}		
	
	
	//=== testing Protocell
	for (uint8_t i=0; i<2; i++){
		uint16_t ir_range = tentacle[i].read_analog_state(0);
		if (ir_range > 1200){
			protocell[i].set_led_level(20);
		}
		else{
			protocell[i].set_led_level(0);
		}
		
	}
	
}

void Behaviours::tentacle_arm_test_behaviour(const uint32_t &curr_time){
	
	//---- Tentacle cycling variables -----
	static uint32_t high_level_ctrl_tentacle_phase_time[3] = {0, 0, 0};


	static uint8_t high_level_ctrl_sma0[3] = {0, 0, 0};
	static uint8_t high_level_ctrl_sma1[3] = {1, 1, 1};
	

	
	//~~~ tentacle cycle~~~~
	for (uint8_t j=0; j<3; j++){
	

		
		if (tentacle_var[j].tentacle_motion_on < 1 && tentacle_var[j].tentacle_cycling < 1){
		
			tentacle[j].set_sma_level(0, 0);
			tentacle[j].set_sma_level(1, 0);
			tentacle_var[j].tentacle_cycling  = 0;
			tentacle_var[j].tentacle_motion_on = 3;
			continue;
		}
		
			
		// starting a cycle
		if (tentacle_var[j].tentacle_cycling < 1){
			
			// behaviour Type
			switch (tentacle_var[j].tentacle_motion_on){
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
			tentacle_var[j].tentacle_cycling = 1; //tentacle_var[j].tentacle_motion_on;
			high_level_ctrl_tentacle_phase_time[j] = millis();  
			
			// turn on the first sma
			tentacle[j].set_sma_level(high_level_ctrl_sma0[j], 255);	
			tentacle[j].set_sma_level(high_level_ctrl_sma1[j], 255);				
		}
		else{
			
			
			volatile uint32_t cycle_time = curr_time - high_level_ctrl_tentacle_phase_time[j];
			
			// if reaches the full period, restart cycle
			if (cycle_time > ((tentacle_var[j].tentacle_arm_cycle_period[1] + tentacle_var[j].tentacle_arm_cycle_period[0]) *100)){
				tentacle_var[j].tentacle_cycling  = 0;
				tentacle_var[j].tentacle_motion_on = 0;
			}
			
			//if reaches the on period 
			else if (cycle_time > (tentacle_var[j].tentacle_arm_cycle_period[0]*100)){
				tentacle[j].set_sma_level(high_level_ctrl_sma1[j], 0);
				tentacle[j].set_sma_level(high_level_ctrl_sma0[j], 0);

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
		indicator_led_blink_cycling = false;

		digitalWrite(indicator_led_pin, 0);
	}
}

void Behaviours::led_wave_behaviour(const uint32_t &curr_time){
	
	
	//static WaveTable test_wave(5);
	wave[0].set_duration(10000);
	uint8_t led_level = wave[0].wave_function(curr_time);
	//protocell.set_led_level(led_level);
	analogWrite(5, led_level);
	

}

void Behaviours::reflex_test_behaviour() {
	
	//=== testing Tentacle ===
	for (uint8_t i=0; i<4; i++){
		uint16_t ir_range = tentacle_var[i].tentacle_ir_state[0];
		if (ir_range > 1200){
			tentacle[i].set_led_level(0, 150);
			tentacle[i].set_led_level(1, 150);
		}
		else{
			tentacle[i].set_led_level(0, 0);
			tentacle[i].set_led_level(1, 0);
		}
	}
}

//----- LOW-LEVEL CONTROL -------
void Behaviours::low_level_control_tentacle_behaviour(){

	
	//>>>> TENTACLE <<<<<
	for (uint8_t j=0; j<3;j++){
		
		tentacle[j].set_sma_level(0, tentacle_var[j].tentacle_sma_level[0]);
		tentacle[j].set_sma_level(1, tentacle_var[j].tentacle_sma_level[1]);
		tentacle[j].set_led_level(0, tentacle_var[j].tentacle_reflex_level[0]);
		tentacle[j].set_led_level(1, tentacle_var[j].tentacle_reflex_level[1]);
	}
}
void Behaviours::low_level_control_tentacle_reflex_led_behaviour(){

	
	//>>>> TENTACLE <<<<<
	for (uint8_t j=0; j<4;j++){
		
		tentacle[j].set_led_level(0, tentacle_var[j].tentacle_reflex_level[0]);
		tentacle[j].set_led_level(1, tentacle_var[j].tentacle_reflex_level[1]);
	}
}

void Behaviours::low_level_control_protocell_behaviour(){
	//>>>> PROTOCELL <<<<<
	for (uint8_t j=0; j<2;j++){
	
		protocell[j].set_led_level(protocell_var[j].protocell_led_level);
	}
	


}

//----- HIGH-LEVEL CONTROL -------
void Behaviours::high_level_control_tentacle_reflex_behaviour(const uint32_t &curr_time){


	//---- Tentacle cycling variables -----
	static uint16_t high_level_ctrl_tentacle_reflex_period[3] = {1000, 1000, 1000};
	
	for (uint8_t j=0; j<3; j++){
	
		
		bool reflex_led_on = false;
		
		//if something is very close
		if (tentacle_var[j].tentacle_ir_state[0] > tentacle_var[j].tentacle_ir_threshold[0]){
			reflex_led_on = true;
			high_level_ctrl_tentacle_reflex_period[j] = tentacle_var[j].tentacle_reflex_period[0];
		}		
		//if there is no object detected
		else{
			reflex_led_on = false;
		}
		
		for (uint8_t i=0; i<2; i++){	
			
			//Actuation
			
			if (reflex_led_on){
				tentacle[j].set_led_level(i, 128);
				// wave[tentacle_var[j].tentacle_reflex_wave_type[i]].set_duration(tentacle_var[j].tentacle_reflex_period[i]);
				// uint8_t reflex_led_level = wave[tentacle_var[j].tentacle_reflex_wave_type[i]].wave_function(curr_time);
				// tentacle[j].set_led_level(i, reflex_led_level);
			}
			else{
				tentacle[j].set_led_level(i, 0);

				// uint8_t reflex_led_level = 0; 
				
				// tentacle[j].set_led_level(i, reflex_led_level);
				// wave[tentacle_var[j].tentacle_reflex_wave_type[i]].restart_wave_function();
			}
		}
		
	}


	
}

void Behaviours::high_level_direct_control_tentacle_arm_behaviour(const uint32_t &curr_time){
	
	//---- Tentacle cycling variables -----
	static uint32_t high_level_ctrl_tentacle_phase_time[3] = {0, 0, 0};


	static uint8_t high_level_ctrl_sma0[3] = {0, 0, 0};
	static uint8_t high_level_ctrl_sma1[3] = {1, 1, 1};
	

	
	//~~~ tentacle cycle~~~~
	for (uint8_t j=0; j<3; j++){
		
		if (tentacle_var[j].tentacle_motion_on < 1 && tentacle_var[j].tentacle_cycling < 1){
		
			tentacle[j].set_sma_level(0, 0);
			tentacle[j].set_sma_level(1, 0);
			tentacle_var[j].tentacle_cycling  = 0;
			continue;
		}
		
			
		// starting a cycle
		if (tentacle_var[j].tentacle_cycling < 1){
			
			// behaviour Type
			switch (tentacle_var[j].tentacle_motion_on){
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
			tentacle_var[j].tentacle_cycling = 1; //tentacle_var[j].tentacle_motion_on;
			high_level_ctrl_tentacle_phase_time[j] = millis();  
			
			// turn on the first sma
			tentacle[j].set_sma_level(high_level_ctrl_sma0[j], 255);	
			tentacle[j].set_sma_level(high_level_ctrl_sma1[j], 255);				
		}
		else{
			
			
			volatile uint32_t cycle_time = curr_time - high_level_ctrl_tentacle_phase_time[j];
			
			// if reaches the full period, restart cycle
			if (cycle_time > ((tentacle_var[j].tentacle_arm_cycle_period[1] + tentacle_var[j].tentacle_arm_cycle_period[0]) *100)){
				tentacle_var[j].tentacle_cycling  = 0;
				tentacle_var[j].tentacle_motion_on = 0;
			}
			
			//if reaches the on period 
			else if (cycle_time > (tentacle_var[j].tentacle_arm_cycle_period[0]*100)){
				tentacle[j].set_sma_level(high_level_ctrl_sma1[j], 0);
				tentacle[j].set_sma_level(high_level_ctrl_sma0[j], 0);

			}
				
		}
		

	}

	
}

void Behaviours::high_level_direct_control_tentacle_arm_behaviour_continuous(const uint32_t &curr_time){
	
	//---- Tentacle cycling variables -----
	static uint32_t high_level_ctrl_tentacle_phase_time[3] = {0, 0, 0};


	static uint8_t high_level_ctrl_sma0[3] = {0, 0, 0};
	static uint8_t high_level_ctrl_sma1[3] = {1, 1, 1};
	

	
	//~~~ tentacle cycle~~~~
	for (uint8_t j=0; j<3; j++){
		
		if (tentacle_var[j].tentacle_motion_on < 1){
		
			tentacle[j].set_sma_level(0, 0);
			tentacle[j].set_sma_level(1, 0);
			continue;
		}
		
			
		// starting a cycle
		if (tentacle_var[j].tentacle_cycling < 1){
			
			// behaviour Type
			switch (tentacle_var[j].tentacle_motion_on){
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
			tentacle_var[j].tentacle_cycling = 1; //tentacle_var[j].tentacle_motion_on;
			high_level_ctrl_tentacle_phase_time[j] = millis();  
			
			// turn on the first sma
			tentacle[j].set_sma_level(high_level_ctrl_sma0[j], 255);	
			tentacle[j].set_sma_level(high_level_ctrl_sma1[j], 255);				
		}
		else{
			
			
			volatile uint32_t cycle_time = curr_time - high_level_ctrl_tentacle_phase_time[j];
			
			// if reaches the full period, restart cycle
			if (cycle_time > ((tentacle_var[j].tentacle_arm_cycle_period[1] + tentacle_var[j].tentacle_arm_cycle_period[0]) *100)){
				tentacle_var[j].tentacle_cycling  = 0;
			}
			
			//if reaches the on period 
			else if (cycle_time > (tentacle_var[j].tentacle_arm_cycle_period[0]*100)){
				tentacle[j].set_sma_level(high_level_ctrl_sma1[j], 0);
				tentacle[j].set_sma_level(high_level_ctrl_sma0[j], 0);

			}
				
		}
		

	}

	
}