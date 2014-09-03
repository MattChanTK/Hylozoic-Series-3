#ifndef _BEHAVIOUR_H
#define _BEHAVIOUR_H

#include "Arduino.h"
#include "teensy_unit.h"



class Behaviours : public TeensyUnit{

	public:
		
		//===============================================
		//==== Constructor and destructor =====
		//===============================================
		
		Behaviours();
		~Behaviours();

		//===============================================
		//==== Communication functions =====
		//===============================================
			
		void parse_msg();
		void compose_reply(byte front_signature, byte back_signature);
		
		//===============================================
		//==== BEHAVIOUR functions =====
		//===============================================
		
		//--- Input functions----
		void sample_inputs();
		
		//---- indicator LED -----
		void led_blink_behaviour(uint32_t curr_time);
		void led_wave_behaviour(uint32_t curr_time);
		
		//----- Protocell reflex -----
		void protocell_reflex(uint32_t curr_time);
		
		//--- Tentacle reflex ----
		void tentacle_reflex(uint32_t curr_time);
		
		//--- sound module reflex ---
		void sound_module_reflex(uint32_t curr_time);
		
		
		//===============================================
		//==== BEHAVIOUR variables =====
		//===============================================
		
		//--- Input Sampling ----
		//~~Teensy on-board~~
		uint16_t analog_0_state = 0;
		//~~IR sensors state~~
		uint16_t ir_0_state = 0;
		uint16_t ir_1_state = 0;
		//~~Ambient light sensor state~~
		uint16_t ambient_light_sensor_state = 0;
		//~~Sound module states~~
		bool sound_detect_state = 0;
		uint16_t sound_module_ir_state = 0;
		
		
		//---- indicator LED blinking -----
		//~~indicator LED on~~
		bool indicator_led_on = true; //exposed
		//~~indicator LED blink~~
		int16_t indicator_led_blink_period = 5000; //exposed
				
		//----- Protocell reflex -----
		//~~output~~
		uint8_t high_power_led_level = 0;  //exposed
		bool high_power_led_reflex_enabled = false;
		uint8_t high_power_led_level_max = 125;
		uint16_t high_power_led_reflex_threshold = 50;
		
		//--- Tentacle reflex ----
		//~~output~~
		bool tentacle_reflex_enabled = true;
		uint8_t sma_0_level = 0; //exposed
		uint8_t sma_1_level = 0; //exposed
		uint8_t reflex_0_level = 0; //exposed
		uint8_t reflex_1_level = 0; //exposed
		uint16_t ir_0_threshold = 150;
		uint16_t ir_1_threshold = 150;
		
		//--- sound module reflex ---
		//~~output~~
		boolean sound_module_reflex_enabled = true;
		
		//--- test wave ----
		WaveTable sma_0_wave;
		
		
		
	private:

		
		

	
};

#endif
