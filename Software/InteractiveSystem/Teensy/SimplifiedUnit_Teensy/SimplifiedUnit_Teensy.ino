
#include "behaviours.h"
#include "teensy_unit.h"


//===========================================================================
//===========================================================================

//===== INITIALIZATION =====

Behaviours test_unit;

void setup() {
	
	//--- Teensy Unit ---
	test_unit.init();
	

}

//===== MAIN LOOP =====

void loop() {
	


	//check for new messages
	if (test_unit.receive_msg()){
			
		// parse the message and save to parameters
		test_unit.parse_msg();

	}

	uint32_t curr_time = millis();
	test_unit.sample_inputs();
    //test_unit.led_blink_behaviour(curr_time);
	//test_unit.led_wave_behaviour(curr_time);
	//test_unit.test_behaviour((const uint32_t) curr_time);
	//test_unit.tentacle_tip_ir_primary_action(curr_time);
	//test_unit.tentacle_bottom_ir_primary_action_soft(curr_time);
	
	test_unit.stress_test_behaviour(curr_time);

}
