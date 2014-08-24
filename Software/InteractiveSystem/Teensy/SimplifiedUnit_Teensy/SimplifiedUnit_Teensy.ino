
#include "teensy_unit.h"
#include "behaviours.h"

//===========================================================================
//===========================================================================

//===== INITIALIZATION =====

TeensyUnit teensy;

void setup() {

	
	//===== clear all existing messages ======
	unsigned long clearing_counter = 0;
	while (teensy.receive_msg()){
	    // this prevents the Teensy from being stuck in infinite loop
	    clearing_counter++;
	    if (clearing_counter>10000){
		break;
           }
	}

}

//===== MAIN LOOP =====

void loop() {

	volatile unsigned long curr_time = millis();
	
	// check for new messages
	if (teensy.receive_msg()){
		
		// parse the message and save to parameters
		//parse_msg(teensy.incomingByte);
	

		teensy.set_led_state(true);
		delay(1000);
		teensy.set_led_state(false);
		delay(150);
	
	}

}
