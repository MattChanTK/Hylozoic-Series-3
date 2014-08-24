#ifndef _BEHAVIOUR_H
#define _BEHAVIOUR_H

#include "Arduino.h"


class Behaviours{

	public:
		
		Behaviours();
		~Behaviours();
		
		//---- Sampling function -----
		void sample_inputs(void);
		
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
	
		//--- Input Sampling ----
		
		//~~Teensy on-board~~
		volatile unsigned int analog_0_state;
		
		//~~IR sensors state~~
		volatile unsigned int ir_0_state;
		volatile unsigned int ir_1_state;
		
		//~~Ambient light sensor state~~
		volatile unsigned int ambient_light_sensor_state;
		
		//~~Sound_moudle states~~
		volatile boolean sound_detect_state;
		volatile unsigned int sound_module_ir_state;
		
		
		//---- indicator LED blinking -----
		
		//~~indicator LED on~~
		volatile boolean indicator_led_on; //exposed
		volatile boolean indicator_led_on_0;
		
		//~~indicator LED blink~~
		IntervalTimer indicator_led_blinkTimer;
		volatile int indicator_led_blinkPeriod_0;
		volatile int indicator_led_blinkPeriod; //exposed
		
		
		//----- Protocell reflex -----
		
		//~~output~~
		volatile unsigned short high_power_led_level;  //exposed
		volatile int high_power_led_reflex_enabled;
		volatile boolean high_power_led_cycling;
		unsigned short high_power_led_level_max;
		volatile unsigned int high_power_led_reflex_threshold;
		
		//~~timing~~
		volatile unsigned long protocell_reflex_phase_time;

		
		//--- Tentacle reflex ----
		
		//~~output~~
		volatile boolean tentacle_reflex_enabled;
		volatile boolean tentacle_reflex_cycling;
		volatile unsigned short sma_0_level; //exposed
		volatile unsigned short sma_1_level; //exposed
		volatile unsigned short reflex_0_level; //exposed
		volatile unsigned short reflex_1_level; //exposed
		volatile unsigned int ir_0_threshold;
		volatile unsigned int ir_1_threshold;
		
		//~~timing~~
		volatile unsigned long tentacle_reflex_phase_time;

		
		//--- sound module reflex ---
		
		//~~output~~
		volatile boolean sound_module_reflex_enabled;
		volatile boolean sound_module_cycling;
		
		//~~timing~~
		volatile unsigned long sound_module_reflex_phase_time;



};

#endif
