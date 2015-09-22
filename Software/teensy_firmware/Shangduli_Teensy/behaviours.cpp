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
		case 254: { 
		
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
		
		// Sound Module low level requests
		case 6: {
		
			uint8_t  device_offset = 2;

			// (8 bytes each)
			// >>>>> byte 2 to byte 9: Sound 0
			// >>>>> byte 10 to byte 17: Sound 1
			// >>>>> byte 18 to byte 25: Sound 2
			// >>>>> byte 26 to byte 33: Sound 3
			// >>>>> byte 34 to byte 41: Sound 4
			// >>>>> byte 41 to byte 49: Sound 2			
			
			for (uint8_t j = 0; j < NUM_SOUND; j++){
				
				const uint8_t byte_offset = 8*(j) + device_offset;
						
				// byte x0 --- sound trig 0
				sound_var[j].trig_state[0] = recv_data_buff[byte_offset+0];
				// byte x1 --- sound trig 1
				sound_var[j].trig_state[1] = recv_data_buff[byte_offset+1];
			
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
	
		// echo
		case 1: {
			
			for (uint8_t i = 2; i<63; i++){

				send_data_buff[i] = recv_data_buff[i];
			}
			break;

		}
		case 2: {
			uint8_t  device_offset = 2;
			
			// (8 bytes each)
			// >>>>> byte 2 to byte 9: Sound 0
			// >>>>> byte 10 to byte 17: Sound 1
			// >>>>> byte 18 to byte 25: Sound 2
			// >>>>> byte 26 to byte 33: Sound 3
			// >>>>> byte 34 to byte 41: Sound 4
			// >>>>> byte 41 to byte 49: Sound 2			
				
			for (uint8_t j = 0; j < NUM_SOUND; j++){
				
				const uint8_t byte_offset = 8*(j) + device_offset;
				
				// byte x0 --- din 0
				for (uint8_t i = 0; i < 2; i++)
					send_data_buff[byte_offset+0+i] = sound_var[j].din_state[0] >> (8*i); 
				
				// byte x2 --- din 1
				for (uint8_t i = 0; i < 2; i++)
					send_data_buff[byte_offset+2+i] = sound_var[j].din_state[1] >> (8*i); 
		
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

	
	//>>>Sound<<<
			
	for (uint8_t j=0; j<NUM_SOUND; j++){
	
		//~~din state~~
		for (uint8_t i=0; i<2; i++){
		
			noInterrupts();
			sound_var[j].din_state[i] = sound[j].read_din_state(i);
			interrupts();
			
		}
		
	}
	
}



//===========================================================================
//============ BEHAVIOUR CODES =========
//===========================================================================

//---- inactive behaviour ----
void Behaviours::inactive_behaviour() {
	
	//=== Sound ===
	for (uint8_t i=0; i<NUM_SOUND; i++){

		sound[i].set_trig_out(0, 0);
		sound[i].set_trig_out(1, 0);
		
	}		
}

//---- test behaviour ----
void Behaviours::test_behaviour(const uint32_t &curr_time) {
	
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

//----- LOW-LEVEL CONTROL -------
void Behaviours::low_level_control_sound_behaviour(){

	//>>>> Sound <<<<<
	for (uint8_t j=0; j<NUM_SOUND; j++){
		
		sound[j].set_trig_out(0, sound_var[j].trig_state[0]);
		sound[j].set_trig_out(1, sound_var[j].trig_state[1]);
		
	}
}

void Behaviours::sound_neighbourhood_behaviour(const uint32_t &curr_time){
	
	//#### Configuration Parameters ####
	const uint16_t LOCAL_DELAY = 0;
	const uint16_t N1_DELAY = 500;
	const uint16_t N2_DELAY = 1000;
	const bool RANDOM_RIPPLE = false;
	const bool REACTOR_MODE_ON = false;
	const uint16_t REACTOR_ACTIVITY_THRES = 4;
	const uint16_t REACTOR_DELAY_RANGE[2] = {0, 10000};
	const uint8_t REACTOR_DURATION = 4;

	//##################################
	
	//>>>> Sound <<<<<
	// Triggering and neighbourhood behaviours
	
	//~~ internal variables ~~~
	bool sound_playing = false;
	
	//~~ internal constants ~~~
	const uint16_t DIN_THRES = 2000;
	const uint16_t DIN_HIGH_THRES = 1500;
	const uint8_t ACTIVE_TYPE_RANGE[2] = {1, 4};
	
	// Sound behaviour
	uint8_t ir_detected = 0;
	for (uint8_t j=0; j<NUM_SOUND; j++){
		
		uint16_t ir_reading = sound_var[j].din_state[0];
		
		// increment activity for each loop having high din_reading
		if (ir_reading > DIN_HIGH_THRES){
			sound_var[j].play_activity += 1;
			ir_detected += 1;
		}
		else{

			if (sound_var[j].play_activity < 0){
				sound_var[j].play_activity = 0;
			}
			else if (sound_var[j].play_activity > 0){
				sound_var[j].play_activity -= 1;
			}
		}
		
		// if high activity
		if (REACTOR_MODE_ON && in_reactor_mode > 0 && sound_var[j].play_delay == 0){
			sound_var[j].play_delay = (uint16_t) random(REACTOR_DELAY_RANGE[0], REACTOR_DELAY_RANGE[1]);
			sound_var[j].play_type = (uint8_t) random(ACTIVE_TYPE_RANGE[0], ACTIVE_TYPE_RANGE[1]);
			sound_var[j].phase_time = curr_time;
			sound_playing = true;
			
			// reset play activitiy
			sound_var[j].play_activity = 0;
		}
		// play sound if detects motion
		else if (ir_reading - sound_var[j].prev_din > DIN_THRES){
						
			sound_var[j].play_delay = 0;
			sound_var[j].play_type = (uint8_t) random(ACTIVE_TYPE_RANGE[0], ACTIVE_TYPE_RANGE[1]);
			sound_var[j].phase_time = curr_time;
			
			
			// trigger neighbours if enough acitivity
			if (sound_var[j].play_activity > 5){
				Serial.printf("[%d] triggers neighbours (level = %d)\n", j, sound_var[j].play_activity);
				// reset play activitiy
				sound_var[j].play_activity = 0;
				
				// find the adjacent sound modules
				uint8_t self_id = sound_spatial_arr[j];
				int8_t left_id = self_id - 1;
				int8_t right_id = self_id + 1;
				int8_t left_id_2 = self_id - 2;
				int8_t right_id_2 = self_id + 2;
				int8_t left_id_3 = self_id - 3;
				int8_t right_id_3 = self_id + 3;
				
				if (left_id >= 0 && sound_var[left_id].play_delay <= 0){
								
					uint8_t play_type;
					if (RANDOM_RIPPLE)
						play_type = sound_var[j].play_type;
					else
						play_type = (uint8_t) random(ACTIVE_TYPE_RANGE[0], ACTIVE_TYPE_RANGE[1]);;
					
					sound_var[left_id].play_delay = N1_DELAY;
					sound_var[left_id].play_type = play_type;
					sound_var[left_id].phase_time = curr_time;
				}
				if (right_id <NUM_SOUND&& sound_var[right_id].play_delay <= 0){
					uint8_t play_type;
					if (RANDOM_RIPPLE)
						play_type = sound_var[j].play_type;
					else
						play_type = (uint8_t) random(ACTIVE_TYPE_RANGE[0], ACTIVE_TYPE_RANGE[1]);;
					
					sound_var[right_id].play_delay = N2_DELAY;
					sound_var[right_id].play_type = play_type;
					sound_var[right_id].phase_time = curr_time;
				}
				if (left_id_2 >= 0 && sound_var[left_id_2].play_delay <= 0){
								
					uint8_t play_type;
					if (RANDOM_RIPPLE)
						play_type = sound_var[j].play_type;
					else
						play_type = (uint8_t) random(ACTIVE_TYPE_RANGE[0], ACTIVE_TYPE_RANGE[1]);;
					
					sound_var[left_id_2].play_delay = N1_DELAY*2;
					sound_var[left_id_2].play_type = play_type;
					sound_var[left_id_2].phase_time = curr_time;
				}
				if (right_id_2 <NUM_SOUND&& sound_var[right_id_2].play_delay <= 0){
					uint8_t play_type;
					if (RANDOM_RIPPLE)
						play_type = sound_var[j].play_type;
					else
						play_type = (uint8_t) random(ACTIVE_TYPE_RANGE[0], ACTIVE_TYPE_RANGE[1]);;
					
					sound_var[right_id_2].play_delay = N2_DELAY*2;
					sound_var[right_id_2].play_type = play_type;
					sound_var[right_id_2].phase_time = curr_time;
				}
				if (left_id_3 >= 0 && sound_var[left_id_3].play_delay <= 0){
								
					uint8_t play_type;
					if (RANDOM_RIPPLE)
						play_type = sound_var[j].play_type;
					else
						play_type = (uint8_t) random(ACTIVE_TYPE_RANGE[0], ACTIVE_TYPE_RANGE[1]);;
					
					sound_var[left_id_3].play_delay = N1_DELAY*2;
					sound_var[left_id_3].play_type = play_type;
					sound_var[left_id_3].phase_time = curr_time;
				}
				if (right_id_3 <NUM_SOUND&& sound_var[right_id_3].play_delay <= 0){
					uint8_t play_type;
					if (RANDOM_RIPPLE)
						play_type = sound_var[j].play_type;
					else
						play_type = (uint8_t) random(ACTIVE_TYPE_RANGE[0], ACTIVE_TYPE_RANGE[1]);;
					
					sound_var[right_id_3].play_delay = N2_DELAY*2;
					sound_var[right_id_3].play_type = play_type;
					sound_var[right_id_3].phase_time = curr_time;
				}
			}
			sound_playing = true;

		}
		
		sound_var[j].prev_din = ir_reading;
	}
	
	// print to serial if there's any activity
	if (sound_playing){
		Serial.printf("%d -- ", curr_time);
		for (uint8_t j=0; j<NUM_SOUND; j++){
			Serial.printf("|[%d] (%d,%d,%d) |", j, sound_var[j].play_delay, sound_var[j].play_type, sound_var[j].prev_din);
		}
		Serial.println();
	}
	
	//decrement in_reactor_mode
	if (REACTOR_MODE_ON){
		if (in_reactor_mode > 0){
			in_reactor_mode -= 1;
			if (in_reactor_mode <= 0){
				Serial.printf("%d -- Deactivated Reactor Mode\n", curr_time);
				in_reactor_mode = 0;
			}
		}
		else{
			//check if entering reactor mode in the next sound
			if (ir_detected >= REACTOR_ACTIVITY_THRES){
				in_reactor_mode = REACTOR_DURATION;
				Serial.printf("%d -- Activated Reactor Mode (level = %d)\n", curr_time, ir_detected);
			}
			else{
			}

		}
	}
	
	// determine the right signal to play
	for (uint8_t j=0; j<NUM_SOUND; j++){
		
		// time to play 
		if (curr_time - sound_var[j].phase_time > sound_var[j].play_delay){
		
			// play the appropiate sound by triggering a couple of pins
			switch(sound_var[j].play_type){
				
				case 1:
					sound_var[j].trig_state[0] = 0;
					sound_var[j].trig_state[1] = 1;
					break;
				case 2:
					sound_var[j].trig_state[0] = 1;
					sound_var[j].trig_state[1] = 0;
					break;
				case 3:
					sound_var[j].trig_state[0] = 0;
					sound_var[j].trig_state[1] = 0;
					break;
				default: // sound off
					sound_var[j].trig_state[0] = 1;
					sound_var[j].trig_state[1] = 1;
					break;
			}
			
			// set play delay to -1 and turning the sound off
			sound_var[j].play_delay = 0;
			sound_var[j].play_type = 0;
			
		}
	}
	//>>>> Sound <<<<<
	// changing the trigger output
	for (uint8_t j=0; j<NUM_SOUND; j++){
		
		sound[j].set_trig_out(0, sound_var[j].trig_state[0]);
		sound[j].set_trig_out(1, sound_var[j].trig_state[1]);
		
	}
	delay(10);

	
}

