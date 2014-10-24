#ifndef _BEHAVIOUR_H
#define _BEHAVIOUR_H

#include "Arduino.h"
#include "teensy_unit.h"



class HK_Behaviours : public TeensyUnit{

	public:
		
		//===============================================
		//==== Constructor and destructor =====
		//===============================================
		
		HK_Behaviours();
		~HK_Behaviours();

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
		void stress_test_behaviour(const uint32_t &curr_time);
		
		//---- indicator LED -----
		void led_blink_behaviour(const uint32_t &curr_time);
		void led_wave_behaviour(const uint32_t &curr_time);
		
		//----- tentacle primary action -----
		void tentacle_tip_ir_primary_action(const uint32_t &curr_time, const uint8_t* type);
		// void tentacle_bottom_ir_primary_action(const uint32_t &curr_time);
		
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
		
		
		//---- indicator LED blinking -----
		//~~indicator LED on~~
		bool indicator_led_on = true; //exposed
		//~~indicator LED blink~~
		int16_t indicator_led_blink_period = 5000; //exposed
				
		
		//>>>Tentacle<<<<
		
		//--- Tentacle tip primary action ----
		
		//~~input~~
		uint8_t tentacle_0_ir_threshold[2] = {240, 100};
		uint8_t tentacle_1_ir_threshold[2] = {240, 100};
		uint8_t tentacle_2_ir_threshold[2] = {240, 100};
		uint8_t* tentacle_ir_threshold[3];
		
		//~~output~~
		uint8_t tentacle_0_cycle_period[2] = {2, 8};
		uint8_t tentacle_1_cycle_period[2] = {2, 8};
		uint8_t tentacle_2_cycle_period[2] = {2, 8};
		uint8_t* tentacle_cycle_period[3];

		uint16_t tentacle_cycle_offset[3] = {500, 500, 500};
		
		
		//--- Tentacle scout primary action ----
		

		
		//--- test wave ----
		WaveTable test_wave;
		
		
		
	private:

		
		

	
};

#endif
