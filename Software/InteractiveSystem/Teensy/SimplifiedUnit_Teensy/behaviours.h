#ifndef _BEHAVIOUR_H
#define _BEHAVIOUR_H

#include "Arduino.h"
#include "teensy_unit.h"


class Behaviours : public TeensyUnit{

	public:
		
		Behaviours();
		~Behaviours();
				
		
		//---- indicator LED -----
		void blink_led(void);
		void led_blink_behaviour(unsigned long curr_time);
		
		//----- Protocell reflex -----
		void protocell_reflex(unsigned long curr_time);
		
		//--- Tentacle reflex ----
		void tentacle_reflex(unsigned long curr_time);
		
		//--- sound module reflex ---
		void sound_module_reflex(unsigned long curr_time);
		
		
	private:
	
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
