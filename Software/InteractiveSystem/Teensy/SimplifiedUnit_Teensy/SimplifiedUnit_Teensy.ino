
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


	// check for new messages
	if (test_unit.receive_msg()){
			
		// parse the message and save to parameters
		test_unit.parse_msg();

	}
	
	volatile unsigned long curr_time = millis();
	//test_unit.led_blink_behaviour(curr_time);
	test_unit.wave_function(curr_time, test_unit.indicator_led_pin, test_unit.indicator_led_wave, 1000, 0.75);

}
