// Set a define here to determine the type of node that is being coded
#define SOUND_NODE

#include "washington_interactive_nodes.h"
#include <SerialCommand.h>

//===== INITIALIZATION =====
#if defined(CRICKET_NODE)
WashingtonCricketNode teensy_unit(0, 2, 5, 3);
#elif defined(FINCRICKET_NODE)
WashingtonFinCricketNode teensy_unit(1, 3, 4, 0, 2, 5);
#elif defined(FIN_NODE)
WashingtonFinNode teensy_unit(1,2,3,4,5,6); //Washington Configuration (1, 3, 4, 0, 2, 5); 
#elif defined(SOUND_NODE)
WashingtonSoundNode teensy_unit(0, 1, 2, 3, 4, 5);
#elif defined(FINLIGHTS_NODE)
FinsSingleLightsUnit teensy_unit(0, 1, 2, 3, 4, 5)
#endif

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

SerialCommand sCmd (&Serial);     // The demo SerialCommand object

void setup() {
	
	//--- Teensy Unit ---
	teensy_unit.init();
	teensy_unit.operation_mode = 0;
	randomSeed(analogRead(A0));


	//--- check msg timer ---
	//set timer in microsecond
	//msg_recv_timer.begin(check_msg, 500); 
	
	Serial.begin(9600);
  delay(1000);
	Serial.println("Setup Done");

  
  sCmd.addCommand("VER",    cmdVersion);          // Prints version
  sCmd.addCommand("BLINK",    cmdBlink);          // Blinks lights
  sCmd.addCommand("PING",    cmdPing);            // Pings the Sound Modules
  sCmd.addCommand("OPMODE",    cmdOperationMode); // Prints the current operation mode
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
volatile uint16_t prev_operation_mode = 0;

void loop() {
  sCmd.readSerial();     // We don't do much, just process serial commands

	if (teensy_unit.receive_msg()){
		
		// parse the message and save to parameters
		teensy_unit.parse_msg();

		loop_since_last_msg = 0;

	}

	
	loop_since_last_msg++;

	
	//teensy_unit.sample_inputs()
	
	if (teensy_unit.operation_mode != prev_operation_mode){
		Serial.print("Operation Mode: ");
		Serial.println(teensy_unit.operation_mode);
		prev_operation_mode = teensy_unit.operation_mode;
	}
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

/* Handling Serial Commands
 *  
 */

void cmdVersion(){
  Serial.println("TEENSY SOFTWARE COMPILED: " __DATE__ " " __TIME__);
}

void cmdBlink(){
  Serial.println("Blinking...");
  for( int i=0; i<10; i++ ){
    #ifndef SOUND_NODE
    teensy_unit.light0.set_output_level(0, 255);
    teensy_unit.light1.set_output_level(2, 0);
    teensy_unit.light2.set_output_level(5, 255);
    delay(25);
    teensy_unit.light0.set_output_level(0, 0);
    teensy_unit.light1.set_output_level(2, 255);
    teensy_unit.light2.set_output_level(5, 0);
    delay(25);
    #else 
    digitalWrite(LED_BUILTIN, LOW);
    delay(25);
    digitalWrite(LED_BUILTIN, HIGH);
    delay(25);
    #endif
  }   
  #ifndef SOUND_NODE
    teensy_unit.light0.set_output_level(0, 0);
    teensy_unit.light1.set_output_level(2, 0);
    teensy_unit.light2.set_output_level(5, 0);
    delay(25);
  #else 
    digitalWrite(LED_BUILTIN, LOW);
  #endif
  Serial.println("Done Blinking...");
}

void cmdPing(){
  Serial.println("Pinging Sound Modules...");
  for( int i=0; i<6; i++ ){
    teensy_unit.sound[i].check_alive();
  }
  Serial.println("Done Pinging...");
}
void cmdOperationMode(){
  Serial.print("Current operation mode: ");
    switch (teensy_unit.operation_mode){
      case 0: 
        Serial.println("self-running test");
        break;
      case 1:
        if (loop_since_last_msg > keep_alive_thres){
          Serial.println("inactive mode");
        }
        else{
          Serial.println("manual mode");
        }
        break;
      default:
        Serial.println("inactive mode");
        break;
  }
}
