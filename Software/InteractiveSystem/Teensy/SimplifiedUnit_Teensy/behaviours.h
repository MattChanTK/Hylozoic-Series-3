#ifndef _BEHAVIOUR_H
#define _BEHAVIOUR_H

#include "Arduino.h"
#include "teensy_unit.h"

#define wave_size 256

typedef prog_uchar PROGMEM const_wave_t;
typedef uint8_t wave_t;

class Behaviours : public TeensyUnit{

	public:
		
		Behaviours();
		~Behaviours();
		
		
		//--- Wave tables ----
		wave_t indicator_led_wave[wave_size] = {
			 128,131,134,137,140,143,146,149,152,156,159,162,165,168,171,174,
			  0,  0,  0,  0,  0,  0,  1,  1,  2,  3,  3,  4,  5,  6,  7,  8, 
			  128,131,134,137,140,143,146,149,152,156,159,162,165,168,171,174,
			  0,  0,  0,  0,  0,  0,  1,  1,  2,  3,  3,  4,  5,  6,  7,  8, 
			  128,131,134,137,140,143,146,149,152,156,159,162,165,168,171,174,
			  0,  0,  0,  0,  0,  0,  1,  1,  2,  3,  3,  4,  5,  6,  7,  8, 
			  128,131,134,137,140,143,146,149,152,156,159,162,165,168,171,174,
			  0,  0,  0,  0,  0,  0,  1,  1,  2,  3,  3,  4,  5,  6,  7,  8, 
			  128,131,134,137,140,143,146,149,152,156,159,162,165,168,171,174,
			  0,  0,  0,  0,  0,  0,  1,  1,  2,  3,  3,  4,  5,  6,  7,  8, 
			  128,131,134,137,140,143,146,149,152,156,159,162,165,168,171,174,
			  0,  0,  0,  0,  0,  0,  1,  1,  2,  3,  3,  4,  5,  6,  7,  8, 
			  0,  0,  0,  0,  0,  0,  1,  1,  2,  3,  3,  4,  5,  6,  7,  8,  
			  9,  10, 12, 13, 15, 16, 18, 19, 21, 23, 25, 27, 29, 31, 33, 35, 
			   0,  0,  0,  0,  0,  0,  1,  1,  2,  3,  3,  4,  5,  6,  7,  8,  
			   0,  0,  0,  0,  0,  0,  1,  1,  2,  3,  3,  4,  5,  6,  7,  8,  
		};
	
		void wave_function(const unsigned long curr_time, const unsigned short pin_num, 
					wave_t (&Wave)[wave_size], const unsigned int duration, const unsigned short amplitude) ;

		
		//---- indicator LED -----
		void led_blink_behaviour(unsigned long curr_time);
		
		//----- Protocell reflex -----
		void protocell_reflex(unsigned long curr_time);
		
		//--- Tentacle reflex ----
		void tentacle_reflex(unsigned long curr_time);
		
		//--- sound module reflex ---
		void sound_module_reflex(unsigned long curr_time);
		
		
		
		
	private:
	
		//---- wave function ----
		volatile bool wave_function_cycling = false;
		volatile unsigned long wave_function_phase_time = 0;
		unsigned int step_duration = 0;
		unsigned int step_count = 0;
	
		//---- indicator LED blinking -----
		//~~indicator LED on~~
		volatile bool indicator_led_state = 0;
		volatile bool indicator_led_on_0 = 1;
		//~~indicator LED blink~~
		volatile bool indicator_led_blink_cycling = false;
		volatile unsigned long indicator_led_blink_phase_time= 0;
		volatile int indicator_led_blink_0 = 100;
		
		//----- Protocell reflex -----
		volatile bool high_power_led_cycling = false;
		volatile unsigned long protocell_reflex_phase_time= 0;
		
		//--- Tentacle reflex ----
		volatile bool tentacle_reflex_cycling = false;
		volatile unsigned long tentacle_reflex_phase_time = 0;

		//--- sound module reflex ---
		volatile bool sound_module_cycling = false;
		volatile unsigned long sound_module_reflex_phase_time = 0;
		

			


};

#endif
