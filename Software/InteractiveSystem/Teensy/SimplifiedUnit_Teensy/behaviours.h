#ifndef _BEHAVIOUR_H
#define _BEHAVIOUR_H

//#include "Arduino.h"
#include "teensy_unit.h"


class Behaviours{

	public:
		
		Behaviours(TeensyUnit &Teensy);
		~Behaviours();
		
		//---- Test Unit Configuration ----
		TeensyUnit &teensy;
		
		
		//---- indicator LED -----
		void blink_led(void);
		void led_blink_behaviour(void);
		
		//----- Protocell reflex -----
		void protocell_reflex(unsigned long curr_time);
		
		//--- Tentacle reflex ----
		void tentacle_reflex(unsigned long curr_time);
		
		//--- sound module reflex ---
		void sound_module_reflex(unsigned long curr_time);
		
		
	private:
	
		//---- indicator LED blinking -----
		//~~indicator LED on~~
		volatile boolean indicator_led_on_0;
		//~~indicator LED blink~~
		IntervalTimer indicator_led_blinkTimer;
		volatile int indicator_led_blinkPeriod_0;
		
		//----- Protocell reflex -----
		volatile boolean high_power_led_cycling;
		volatile unsigned long protocell_reflex_phase_time;
		
		//--- Tentacle reflex ----
		volatile boolean tentacle_reflex_cycling;
		volatile unsigned long tentacle_reflex_phase_time;

		//--- sound module reflex ---
		volatile boolean sound_module_cycling;
		volatile unsigned long sound_module_reflex_phase_time;

			


};

#endif
