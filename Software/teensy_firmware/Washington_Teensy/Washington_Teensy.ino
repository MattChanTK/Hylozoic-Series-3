#include "cbla_test_bed.h"
#include "teensy_unit.h"


//===========================================================================
//===========================================================================

//===== INITIALIZATION =====

CBLATestBed teensy_unit;

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
	//teensy_unit.operation_mode = 0;
	randomSeed(analogRead(A0));
	
	//--- check msg timer ---
	//set timer in microsecond
	//msg_recv_timer.begin(check_msg, 500); 
}


//===== Behaviours Sets ======

void manual_control(){
	uint32_t curr_time = get_time();
	
	teensy_unit.high_level_direct_control_fin_arm_behaviour(curr_time);
	teensy_unit.low_level_control_fin_reflex_behaviour();
	teensy_unit.low_level_control_light_behaviour();

}

void internode_test() {

	uint32_t curr_time = get_time();
	//teensy_unit.sample_inputs();
	
	teensy_unit.high_level_direct_control_fin_arm_behaviour(curr_time);
	teensy_unit.low_level_control_fin_reflex_behaviour();

	

}

void system_identification() {

	uint32_t curr_time = get_time();
	//teensy_unit.sample_inputs();
	
	teensy_unit.high_level_direct_control_fin_arm_behaviour(curr_time);
	teensy_unit.low_level_control_fin_reflex_behaviour();
	teensy_unit.low_level_control_light_behaviour();
	

}

void cbla(){
	uint32_t curr_time = get_time();
	//teensy_unit.sample_inputs();
	
	teensy_unit.high_level_direct_control_fin_arm_behaviour(curr_time);
	teensy_unit.low_level_control_fin_reflex_behaviour();
	teensy_unit.low_level_control_light_behaviour();

}

void cbla2(){
	uint32_t curr_time = get_time();
	//teensy_unit.sample_inputs();
	
	teensy_unit.low_level_control_fin_behaviour();
	teensy_unit.low_level_control_fin_reflex_behaviour();
	teensy_unit.low_level_control_light_behaviour();

}

void cbla2_manual(){
	cbla2();
}

void cbla2_prescripted(){
	cbla2();
}

void self_running_test(){
	uint32_t curr_time = get_time();
	teensy_unit.sample_inputs();

	teensy_unit.fin_arm_test_behaviour(curr_time);
	teensy_unit.reflex_test_behaviour();
	teensy_unit.low_level_control_light_behaviour();
}

void quality_assurance(){

	uint32_t curr_time = get_time();
	
	teensy_unit.high_level_direct_control_fin_arm_behaviour_continuous(curr_time);
	teensy_unit.low_level_control_fin_reflex_behaviour();
	teensy_unit.low_level_control_light_behaviour();
}	

void preprogrammed_behaviour(){
	cbla();
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
	
	
	switch (teensy_unit.operation_mode){
	
		case 0: 
			self_running_test();
			break;
		case 1:
			manual_control();
			break;
		case 2:
			if (loop_since_last_msg < keep_alive_thres)
				system_identification();
			else
				inactive_mode();
			break;
		case 3:
			if (loop_since_last_msg < keep_alive_thres)
				cbla();
			else
				inactive_mode();
			break;
		case 4:
			internode_test();
			break;
		case 5:
			if (loop_since_last_msg < keep_alive_thres)
				preprogrammed_behaviour();
			else
				inactive_mode();
			break;
		case 6:
			quality_assurance();
			break;
		case 7:
			if (loop_since_last_msg < keep_alive_thres)
				cbla2();
			else
				inactive_mode();			
			break;
		case 8:
			if (loop_since_last_msg < keep_alive_thres)
				cbla2_manual();
			else
				inactive_mode();			
			break;
		case 9:
			if (loop_since_last_msg < keep_alive_thres)
				cbla2_prescripted();
			else
				inactive_mode();			
			break;
		default:
			inactive_mode();
			break;
	
	}
	


}

