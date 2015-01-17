
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

//===== MAIN LOOP =====

void loop() {
	
	
	//check for new messages
	if (teensy_unit.receive_msg()){
			
		// parse the message and save to parameters
		teensy_unit.parse_msg();

	}


	uint32_t curr_time = millis();
	teensy_unit.sample_inputs();
	//teensy_unit.led_blink_behaviour(curr_time);
	//teensy_unit.low_level_control_tentacle_behaviour(curr_time);
	//teensy_unit.high_level_control_tentacle_arm_behaviour(curr_time);
	//teensy_unit.high_level_control_tentacle_reflex_behaviour(curr_time);
	
	teensy_unit.low_level_control_protocell_behaviour(curr_time);
	teensy_unit.high_level_direct_control_tentacle_arm_behaviour(curr_time);

	//teensy_unit.led_wave_behaviour(curr_time);
	//teensy_unit.test_behaviour((const uint32_t) curr_time);
	teensy_unit.reflex_test_behaviour();

	

	
	//teensy_unit.stress_test_behaviour(curr_time);
	
			
}
