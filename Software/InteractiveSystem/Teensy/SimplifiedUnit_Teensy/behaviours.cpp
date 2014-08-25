#include "behaviours.h"


//===========================================================================
//===== CONSTRUCTOR and DECONSTRUCTOR =====
//===========================================================================

Behaviours::Behaviours()
{
	
	
}

Behaviours::~Behaviours(){
	
}

//===========================================================================
//============ BEHAVIOUR CODES =========
//===========================================================================


//--- Wave Table Synthesis ---
//void wave_function(pin_num, wave_table, speed, amplitude){
//
//}


//---- indicator LED -----

void Behaviours::led_blink_behaviour(unsigned long curr_time){
	if (indicator_led_on){
		
		// starting a blink cycle
		if (indicator_led_blink_cycling == false){
			indicator_led_blink_cycling = true;
			indicator_led_blink_phase_time = millis();      
			digitalWrite(indicator_led_pin, 1);
		}
		else if (indicator_led_blink_cycling == true){
			
			// if reaches the full period, restart cycle
			if ((curr_time - indicator_led_blink_phase_time) > indicator_led_blink_period){
				indicator_led_blink_cycling = false;
			}
			// if reaches half the period, turn it off
			else if ((curr_time - indicator_led_blink_phase_time) > indicator_led_blink_period>>1){
				digitalWrite(indicator_led_pin, 0);
			}	
		}
	}
	else{
	
		// if stopped in the middle of a cycle
		if (indicator_led_blink_cycling){
			indicator_led_blink_cycling = false;
			digitalWrite(indicator_led_pin, 0);
		}
	}
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




