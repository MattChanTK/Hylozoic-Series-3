#include "behaviours.h"
#include "teensy_unit.h"


//===========================================================================
//===========================================================================

//===== INITIALIZATION =====

Behaviours teensy_unit;

//===== check for messages periodically =====

// Create an IntervalTimer object 
IntervalTimer msg_recv_timer;

//check for new messages
void check_msg(){
	
	if (teensy_unit.receive_msg()){
			
		// parse the message and save to parameters
		teensy_unit.parse_msg();

	}
}

//get time that cannot be interrupted
uint32_t get_time(){
	//noInterrupts();
	uint32_t curr_time = millis();
	//interrupts();
	return curr_time;

}

void setup() {
	
	//--- Teensy Unit ---
	teensy_unit.init();
	randomSeed(analogRead(A0));
	
	//--- check msg timer ---
	//set timer in microsecond
	//msg_recv_timer.begin(check_msg, 500); 
}


//===== Behaviours Sets ======

void manual_control(){
	uint32_t curr_time = get_time();
	
	teensy_unit.high_level_direct_control_tentacle_arm_behaviour(curr_time);
	teensy_unit.low_level_control_tentacle_reflex_led_behaviour();
	teensy_unit.low_level_control_protocell_behaviour();

}

void internode_test() {

	uint32_t curr_time = get_time();
	//teensy_unit.sample_inputs();
	
	teensy_unit.high_level_direct_control_tentacle_arm_behaviour(curr_time);
	teensy_unit.low_level_control_tentacle_reflex_led_behaviour();

	

}

void system_identification() {

	uint32_t curr_time = get_time();
	//teensy_unit.sample_inputs();
	
	teensy_unit.high_level_direct_control_tentacle_arm_behaviour(curr_time);
	teensy_unit.low_level_control_tentacle_reflex_led_behaviour();
	teensy_unit.low_level_control_protocell_behaviour();
	

}

void cbla(){
	uint32_t curr_time = get_time();
	//teensy_unit.sample_inputs();
	
	teensy_unit.high_level_direct_control_tentacle_arm_behaviour(curr_time);
	teensy_unit.low_level_control_tentacle_reflex_led_behaviour();
	teensy_unit.low_level_control_protocell_behaviour();

}

void self_running_test(){
	uint32_t curr_time = get_time();
	teensy_unit.sample_inputs();

	teensy_unit.tentacle_arm_test_behaviour(curr_time);
	teensy_unit.reflex_test_behaviour();
	teensy_unit.low_level_control_protocell_behaviour();
	teensy_unit.sma_control(curr_time);
}

void quality_assurance(){

	uint32_t curr_time = get_time();
	
	teensy_unit.high_level_direct_control_tentacle_arm_behaviour_continuous(curr_time);
	teensy_unit.low_level_control_tentacle_reflex_led_behaviour();
	teensy_unit.low_level_control_protocell_behaviour();
}	

void preprogrammed_behaviour(){

}

void inactive_mode(){

}

//===== MAIN LOOP =====

void loop() {


	if (teensy_unit.receive_msg()){
			
		// parse the message and save to parameters
		teensy_unit.parse_msg();

	}
	
	//teensy_unit.sample_inputs();
	
	
	switch (teensy_unit.operation_mode){
	
		case 0: 
			self_running_test();
			break;
		case 1:
			manual_control();
			break;
		case 2:
			system_identification();
			break;
		case 3:
			cbla();
			break;
		case 4:
			internode_test();
			break;
		case 5:
			preprogrammed_behaviour();
			break;
		case 6:
			quality_assurance();
			break;
		default:
			inactive_mode();
			break;
	
	}
	


}

