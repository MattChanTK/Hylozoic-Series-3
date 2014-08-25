
#include "behaviours.h"
#include "teensy_unit.h"

//===========================================================================
//===========================================================================

//===== INITIALIZATION =====

TeensyUnit teensy;
Behaviours test_unit(teensy);

void setup() {

	//--- Teensy Unit ---
	teensy.init();

}

//===== MAIN LOOP =====

void loop() {

	volatile unsigned long curr_time = millis();
	
	// check for new messages
	if (teensy.receive_msg()){
		
		// parse the message and save to parameters
		teensy.parse_msg();
	

		teensy.set_led_state();
		
	}

}
