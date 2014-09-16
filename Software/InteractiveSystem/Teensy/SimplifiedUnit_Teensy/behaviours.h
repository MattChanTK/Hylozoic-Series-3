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
		
		//--- Input functions----
		void sample_inputs();
		
		//===============================================
		//==== BEHAVIOUR functions =====
		//===============================================
		
		//---- test behaviour ----
		void test_behaviour(const uint32_t &curr_time);
		
		//---- indicator LED -----
		void led_blink_behaviour(const uint32_t &curr_time);
		void led_wave_behaviour(const uint32_t &curr_time);
		
		//----- Protocell reflex -----
		void protocell_reflex(const uint32_t &curr_time);
		
		//--- Tentacle reflex ----
		void tentacle_reflex(const uint32_t &curr_time);
	
		
		//===============================================
		//==== BEHAVIOUR variables =====
		//===============================================
		
		//--- Input Sampling ----
		
		//>>>Tentacle<<<<
		//~~IR sensors state~~
		uint8_t tentacle_0_ir_state[2] = {0, 0};
		uint8_t tentacle_1_ir_state[2] = {0, 0};
		uint8_t tentacle_2_ir_state[2] = {0, 0};
		uint8_t* tentacle_ir_state[3];
		
		//~~Accelerometer state~~ 
		int16_t tentacle_0_acc_state[3]; // {x,y,z}
		int16_t tentacle_1_acc_state[3]; // {x,y,z}
		int16_t tentacle_2_acc_state[3]; // {x,y,z}
		int16_t* tentacle_acc_state[3];
	
		//>>>protocell<<<
		//~~Ambient light sensor state~~
		uint8_t protocell_ambient_light_sensor_state;

		
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
		
		
		//--- test wave ----
		WaveTable test_wave;
		
		
		
	private:

		
		

	
};

#endif
