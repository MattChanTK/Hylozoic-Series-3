#ifndef _BEHAVIOUR_H
#define _BEHAVIOUR_H

#include "Arduino.h"
#include "teensy_unit.h"

#define wave_size 32

typedef prog_uchar PROGMEM const_wave_t;
typedef uint8_t wave_t;

class Behaviours : public TeensyUnit{

	public:
		
		Behaviours();
		~Behaviours();
		
		
		//--- Wave tables ----
		wave_t indicator_led_wave[wave_size] = {
			255,255,255,255,255,255,255,255,
			128,128,128,128,128,128,128,128,
			255,255,255,255,255,255,255,255,
			0,  0,  0,  0,  0,  0,  0,  0,  
		};
	
		void wave_function(const uint32_t curr_time, const uint8_t pin_num, 
					const wave_t (&Wave)[wave_size], const uint16_t duration, const float amplitude) ;

		
		//---- indicator LED -----
		void led_blink_behaviour(uint32_t curr_time);
		
		//----- Protocell reflex -----
		void protocell_reflex(uint32_t curr_time);
		
		//--- Tentacle reflex ----
		void tentacle_reflex(uint32_t curr_time);
		
		//--- sound module reflex ---
		void sound_module_reflex(uint32_t curr_time);
		
		
		
		
	private:
	
		//---- wave function ----
		bool wave_function_cycling = false;
		uint32_t wave_function_phase_time = 0;
		uint16_t step_duration = 0;
		uint16_t step_count = 0;
	
		//---- indicator LED blinking -----
		//~~indicator LED on~~
		bool indicator_led_state = 0;
		bool indicator_led_on_0 = 1;
		//~~indicator LED blink~~
		bool indicator_led_blink_cycling = false;
		uint32_t indicator_led_blink_phase_time= 0;
		int indicator_led_blink_0 = 100;
		
		//----- Protocell reflex -----
		bool high_power_led_cycling = false;
		uint32_t protocell_reflex_phase_time= 0;
		
		//--- Tentacle reflex ----
		bool tentacle_reflex_cycling = false;
		uint32_t tentacle_reflex_phase_time = 0;

		//--- sound module reflex ---
		bool sound_module_cycling = false;
		uint32_t sound_module_reflex_phase_time = 0;
		

			


};

#endif
