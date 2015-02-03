
#include "behaviours.h"
#include "teensy_unit.h"


//===========================================================================
//===========================================================================

//===== INITIALIZATION =====

Behaviours teensy_unit;

void setup() {
	
	//--- Teensy Unit ---
	teensy_unit.init();
	randomSeed(analogRead(A0));


}

//===== Behaviours Sets ======

void manual_control(){
	uint32_t curr_time = millis();
	
	teensy_unit.high_level_direct_control_tentacle_arm_behaviour(curr_time);
	teensy_unit.low_level_control_tentacle_reflex_led_behaviour(curr_time);
	teensy_unit.low_level_control_protocell_behaviour(curr_time);

}

void internode_test() {

	uint32_t curr_time = millis();
	//teensy_unit.sample_inputs();
	
	teensy_unit.high_level_direct_control_tentacle_arm_behaviour(curr_time);
	teensy_unit.low_level_control_tentacle_reflex_led_behaviour(curr_time);

	

}

void system_identification() {

	uint32_t curr_time = millis();
	//teensy_unit.sample_inputs();
	
	teensy_unit.high_level_direct_control_tentacle_arm_behaviour(curr_time);
	teensy_unit.low_level_control_tentacle_reflex_led_behaviour(curr_time);
	teensy_unit.low_level_control_protocell_behaviour(curr_time);
	

}

void cbla(){
	int32_t curr_time = millis();
	//teensy_unit.sample_inputs();
	
	teensy_unit.high_level_direct_control_tentacle_arm_behaviour(curr_time);
	teensy_unit.low_level_control_tentacle_reflex_led_behaviour(curr_time);
	teensy_unit.low_level_control_protocell_behaviour(curr_time);

}

void self_running_test(){
	int32_t curr_time = millis();
	teensy_unit.sample_inputs();

	teensy_unit.tentacle_arm_test_behaviour(curr_time);
	teensy_unit.reflex_test_behaviour();
	teensy_unit.low_level_control_protocell_behaviour(curr_time);
}

void preprogrammed_behaviour(){

}

void inactive_mode(){

}

//===== MAIN LOOP =====

void loop() {
	
	
	//check for new messages
	if (teensy_unit.receive_msg()){
			
		// parse the message and save to parameters
		teensy_unit.parse_msg();

	}

	
	//internode_test();
	
	//system_identification();
	
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
		default:
			inactive_mode();
			break;
	
	}
	

	
	//self_running_test();

	
		
}

