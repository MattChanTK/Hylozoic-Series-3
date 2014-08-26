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
void Behaviours::wave_function(const uint32_t curr_time, const uint8_t pin_num, 
					const wave_t (&Wave)[wave_size], const uint16_t duration, const float amplitude) {
	

	// starting a wave cycle
	if (wave_function_cycling == false){

		wave_function_cycling = true;
		wave_function_phase_time = millis();
		step_duration = duration/wave_size ;
		step_count = 1;
		
		analogWrite(pin_num, (uint8_t) Wave[0]*amplitude);
	}
	else if (wave_function_cycling == true){
	
		// if reaches full time duration
		if (step_count >= wave_size  || (curr_time - wave_function_phase_time) > duration){
			wave_function_cycling = false;
		}
		// if reaches one time step
		if ((curr_time - wave_function_phase_time) > step_count*step_duration){
			step_count++;
			analogWrite(pin_num, (uint8_t) Wave[step_count]*amplitude);
		}
	}
	
}


//---- indicator LED -----

void Behaviours::led_blink_behaviour(uint32_t curr_time) {
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
void Behaviours::protocell_reflex(uint32_t curr_time){

}

//--- Tentacle reflex ----
void Behaviours::tentacle_reflex(uint32_t curr_time){

}

//--- sound module reflex ---
void Behaviours::sound_module_reflex(uint32_t curr_time){

}




