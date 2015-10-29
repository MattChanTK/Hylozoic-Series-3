#include "washington_interactive_nodes.h"

//===========================================================================
//===========================================================================

//===== INITIALIZATION =====
WashingtonCricketNode teensy_unit(0, 2, 5, 3);
//WashingtonFinCricketNode teensy_unit(1, 3, 4, 0, 2, 5);
//WashingtonFinNode teensy_unit(1, 3, 4, 0, 2, 5);
//WashingtonSoundNode teensy_unit(0, 1, 2, 3, 4, 5);

//check for new messages
void check_msg(){
	
	if (teensy_unit.receive_msg()){
			
		// parse the message and save to parameters
		teensy_unit.parse_msg();

	}
}

//get time that cannot be interrupted
uint32_t get_time(){
	noInterrupts();
	uint32_t curr_time = millis();
	interrupts();
	return curr_time;

}

void setup() {
	
	//--- Teensy Unit ---
	teensy_unit.init();
	teensy_unit.operation_mode = 0;
	randomSeed(analogRead(A0));


	//--- check msg timer ---
	//set timer in microsecond
	//msg_recv_timer.begin(check_msg, 500); 
	
	Serial.begin(9600);
	Serial.print("Setup Done");

}


//===== Behaviours Sets ======


void self_running_test(){
	uint32_t curr_time = get_time();
	teensy_unit.sample_inputs();

	// teensy_unit.test_behaviour(curr_time);
	// teensy_unit.led_blink_behaviour(curr_time);
	// delay(100);
	teensy_unit.self_running_behaviour(curr_time);
}
void manual_mode(){
	uint32_t curr_time = get_time();

	teensy_unit.low_level_control_behaviour(curr_time);

}
void inactive_mode(){
	
	teensy_unit.inactive_behaviour();

}

//===== MAIN LOOP =====

uint16_t loop_since_last_msg = 0;
const uint16_t keep_alive_thres = 2000;

void loop() {

	if (teensy_unit.receive_msg()){
		
		// parse the message and save to parameters
		teensy_unit.parse_msg();

		loop_since_last_msg = 0;

	}

	
	loop_since_last_msg++;

	
	//teensy_unit.sample_inputs();
	
	//Serial.println(teensy_unit.operation_mode);
	switch (teensy_unit.operation_mode){
	
		case 0: 
			self_running_test();
			break;
			
		case 1:
			if (loop_since_last_msg > keep_alive_thres){
				inactive_mode();
			}
			else{
				manual_mode();
			}
			break;
		
		default:
			inactive_mode();
			break;
	
	}

}

