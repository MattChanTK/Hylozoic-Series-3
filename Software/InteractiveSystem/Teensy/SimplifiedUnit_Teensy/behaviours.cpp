#include "behaviours.h"


//===========================================================================
//===== CONSTRUCTOR and DECONSTRUCTOR =====
//===========================================================================

Behaviours::Behaviours(){
	
}

Behaviours::~Behaviours(){
	
}

//===========================================================================
//============ BEHAVIOUR CODES =========
//===========================================================================

//---- indicator LED -----

void Behaviours::led_blink_behaviour(uint32_t curr_time) {

	//---- indicator LED blinking variables -----
	//~~indicator LED on~~
	static bool indicator_led_state = 0;
	static bool indicator_led_on_0 = 1;
	//~~indicator LED blink~~
	static bool indicator_led_blink_cycling = false;
	static uint32_t indicator_led_blink_phase_time= 0;

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

void Behaviours::led_wave_behaviour(uint32_t curr_time){
	
	
	static WaveTable test_wave(5);
	test_wave.set_duration(10000);
	test_wave.set_amplitude(1.0);
	test_wave.wave_function(curr_time);
	

}

//----- Protocell reflex -----
void Behaviours::protocell_reflex(uint32_t curr_time){
	//----- Protocell reflex -----
	static bool high_power_led_cycling = false;
	static uint32_t protocell_reflex_phase_time= 0;

}

//--- Tentacle reflex ----
void Behaviours::tentacle_reflex(uint32_t curr_time){
	//--- Tentacle reflex ----
	static bool tentacle_reflex_cycling = false;
	static uint32_t tentacle_reflex_phase_time = 0;
}

//--- sound module reflex ---
void Behaviours::sound_module_reflex(uint32_t curr_time){
	//--- sound module reflex ---
	static	bool sound_module_cycling = false;
	static	uint32_t sound_module_reflex_phase_time = 0;

}




