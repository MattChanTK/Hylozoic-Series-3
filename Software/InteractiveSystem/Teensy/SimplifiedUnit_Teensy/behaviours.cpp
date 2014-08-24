#include "behaviours.h"


//===========================================================================
//===== CONSTRUCTOR and DECONSTRUCTOR =====
//===========================================================================

Behaviours::Behaviours(){

	//--- Input Sampling ----
	//~~Teensy on-board~~
	analog_0_state = 0;
	//~~IR sensors state~~
	ir_0_state = 0;
	ir_1_state = 0;
	//~~Ambient light sensor state~~
	ambient_light_sensor_state = 0;
	//~~Sound_moudle states~~
	sound_detect_state = 0;
	sound_module_ir_state = 0;
	
	//---- indicator LED blinking -----
	//~~indicator LED on~~
	indicator_led_on = false; //exposed
	indicator_led_on_0 = false;
	//~~indicator LED blink~~
	indicator_led_blinkPeriod_0 = -99;
	indicator_led_blinkPeriod = 0; //exposed
	
	
	//----- Protocell reflex -----
	//~~output~~
	high_power_led_level = 5;  //exposed
	high_power_led_reflex_enabled = true;
	high_power_led_cycling = false;
	high_power_led_level_max = 125;
	high_power_led_reflex_threshold = 50;
	//~~timing~~
	protocell_reflex_phase_time;
	
	//--- Tentacle reflex ----
	//~~output~~
	tentacle_reflex_enabled = true;
	tentacle_reflex_cycling = false;
	sma_0_level = 0; //exposed
	sma_1_level = 0; //exposed
	reflex_0_level = 10; //exposed
	reflex_1_level = 10; //exposed
	ir_0_threshold = 150;
	ir_1_threshold = 150;
	//~~timing~~
	tentacle_reflex_phase_time;
	
	//--- sound module reflex ---
	//~~output~~
	sound_module_reflex_enabled = true;
	sound_module_cycling = false;
	//~~timing~~
	sound_module_reflex_phase_time;
	
	
}

Behaviours::~Behaviours(){
	
}

//===========================================================================
//============ BEHAVIOUR CODES =========
//===========================================================================


//--- Sampling function ---
void Behaviours::sample_inputs(){
	// analog_0_state = analogRead(analog_0_pin);
	// ambient_light_sensor_state = analogRead(ambient_light_sensor_pin);
	// ir_0_state = analogRead(ir_0_pin);
	// ir_1_state = analogRead(ir_1_pin);
}


//--- Wave Table Synthesis ---
//void wave_function(pin_num, wave_table, speed, amplitude){
//
//}


//---- Sampling function -----
void Behaviours::blink_led(void){
	// ledState ^= 1;
	// digitalWrite(indicator_led_pin, ledState);  
}

//---- indicator LED -----
void Behaviours::led_blink_behaviour(){
	// //..... indicator LED .....
	// // if it should be on
	// if (indicator_led_on == 1){
		
		// // if there is a change in blink period
		// if (indicator_led_blinkPeriod != indicator_led_blinkPeriod_0 ||
				// indicator_led_on != indicator_led_on_0){
			// indicator_led_on_0 = indicator_led_on;
			// indicator_led_blinkPeriod_0 = indicator_led_blinkPeriod;
			
			// //update the blinker's period
			// if (indicator_led_blinkPeriod > 0){
				// indicator_led_blinkTimer.begin(blinkLED, indicator_led_blinkPeriod);
			// }
			// //if the period is 0 just end the blink timer and and turn it on 
			// else if (indicator_led_blinkPeriod == 0){
				// indicator_led_blinkTimer.end();
				// ledState = 1;
				// digitalWrite(indicator_led_pin, ledState);
			// }
		// }
	// }
	// // if it should be off
	// else if (indicator_led_on == 0){ 
		// indicator_led_on_0 = indicator_led_on;
		// // end the blink timer and turn it off
		// indicator_led_blinkTimer.end();
		// ledState = 0;
		// digitalWrite(indicator_led_pin, ledState);
	// }
}

//----- Protocell reflex -----
void Behaviours::protocell_reflex(unsigned long curr_time){
	// if (high_power_led_reflex_enabled){
		
		// ambient_light_sensor_state = analogRead(ambient_light_sensor_pin);
		
		// if (high_power_led_cycling == false && 
                    // sound_module_ir_state > 300){
			// //	ambient_light_sensor_state < high_power_led_reflex_threshold){
			// high_power_led_cycling = true;
			// protocell_reflex_phase_time = millis();       
		// }
		// else if (high_power_led_cycling == true){
			// if ((curr_time - protocell_reflex_phase_time) < 2000){
				// analogWrite(high_power_led_pin, high_power_led_level);
			// }
			// else if ((curr_time - protocell_reflex_phase_time) < 4000){
				// analogWrite(high_power_led_pin, 0);
			// }
                        // else{
				// high_power_led_cycling = false;
				// analogWrite(high_power_led_pin, 0);
			// }
		// }
	// }
}

//--- Tentacle reflex ----
void Behaviours::tentacle_reflex(unsigned long curr_time){
	// if (tentacle_reflex_enabled){
		// ir_0_state = analogRead(ir_0_pin);
		// ir_1_state = analogRead(ir_1_pin);
		
		// if (tentacle_reflex_cycling == false &&
			// ir_0_state > ir_0_threshold){   
			
			// tentacle_reflex_cycling = true;
			// tentacle_reflex_phase_time = millis();  
	
		// }
		// else if (tentacle_reflex_cycling == true){
			// if ((curr_time - tentacle_reflex_phase_time) < 1500){
				// analogWrite(sma_0_pin, sma_0_level);
				// analogWrite(sma_1_pin, sma_1_level);
			// }
			// else if ((curr_time - tentacle_reflex_phase_time) < 5000)
			// {
				// analogWrite(sma_0_pin, 0);
				// analogWrite(sma_1_pin, 0);
			// }
			// else{
				// tentacle_reflex_cycling = false;
				// analogWrite(sma_0_pin, 0);
				// analogWrite(sma_1_pin, 0);
			// }
		// }
		// if (ir_0_state > ir_1_threshold){
			// analogWrite(reflex_0_pin, reflex_0_level);
			// analogWrite(reflex_1_pin, reflex_1_level);
		// }
		// else{
			// analogWrite(reflex_0_pin, 0);
			// analogWrite(reflex_1_pin, 0);
		// }
               
	// }
}

//--- sound module reflex ---
void Behaviours::sound_module_reflex(unsigned long curr_time){
	// if (sound_module_reflex_enabled){
		
		// sound_module_ir_state = analogRead(sound_module_ir_pin);
		// //sound_detect_state = digitalRead(sound_detect_pin);
		
		// if (sound_module_cycling == false && 
			// //sound_detect_state == true){
			// sound_module_ir_state > 300){
			// sound_module_cycling = true;
			// sound_module_reflex_phase_time = millis();       
		// }
		// else if (sound_module_cycling == true){
			// if ((curr_time - sound_module_reflex_phase_time) < 50){
				// digitalWrite(sound_trigger_pin, 1);
			// }
			// else if ((curr_time - sound_module_reflex_phase_time) < 100){
				// digitalWrite(sound_trigger_pin, 0);
			// }
			// else{
				// sound_module_cycling = false;
				// digitalWrite(sound_trigger_pin, 0);
			// }
		// }
	// }
}




