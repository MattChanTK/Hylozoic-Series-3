
#include "HK_behaviours.h"
#include "teensy_unit.h"


//===========================================================================
//===========================================================================

//===== INITIALIZATION =====

HK_Behaviours hk_unit;

void setup() {
	
	//--- Teensy Unit ---
	hk_unit.init();
	randomSeed(analogRead(A0));

}

//===== MAIN LOOP =====

void loop() {
	

	//check for new messages
	if (hk_unit.receive_msg()){
			
		// parse the message and save to parameters
		hk_unit.parse_msg();

	}

	uint32_t curr_time = millis();
	hk_unit.sample_inputs();
    //hk_unit.led_blink_behaviour(curr_time);
	//hk_unit.led_wave_behaviour(curr_time);
	//hk_unit.test_behaviour((const uint32_t) curr_time);
	
	uint8_t tentacle_action_type[3] = {255,255,255}; // random type
	hk_unit.tentacle_tip_ir_primary_action(curr_time, tentacle_action_type);
	
	hk_unit.tentacle_scout_ir_primary_action(curr_time);
	
	//hk_unit.stress_test_behaviour(curr_time);
	
			
}
