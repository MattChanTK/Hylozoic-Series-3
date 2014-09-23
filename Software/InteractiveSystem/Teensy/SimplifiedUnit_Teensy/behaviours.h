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
		
		//----- tentacle primary action -----
		void tentacle_tip_ir_primary_action(const uint32_t &curr_time);
		void tentacle_bottom_ir_primary_action(const uint32_t &curr_time);
		void tentacle_bottom_ir_primary_action_soft(const uint32_t &curr_time);
		
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
		uint8_t protocell_0_ambient_light_sensor_state[1] = {0};
		uint8_t protocell_1_ambient_light_sensor_state[1] = {0};
		uint8_t* protocell_ambient_light_sensor_state[2];
		
		//---- indicator LED blinking -----
		//~~indicator LED on~~
		bool indicator_led_on = true; //exposed
		//~~indicator LED blink~~
		int16_t indicator_led_blink_period = 5000; //exposed
				
		
		//>>>Tentacle<<<<
		
		//--- Tentacle tip primary action ----
		//~~output~~

		uint8_t tentacle_0_ir_threshold[2] = {240, 100};
		uint8_t tentacle_1_ir_threshold[2] = {240, 100};
		uint8_t tentacle_2_ir_threshold[2] = {240, 100};
		uint8_t* tentacle_ir_threshold[3];
		
		uint8_t tentacle_0_cycle_period[2] = {2, 8};
		uint8_t tentacle_1_cycle_period[2] = {2, 8};
		uint8_t tentacle_2_cycle_period[2] = {2, 8};
		uint8_t* tentacle_cycle_period[3];
		
		
		//--- test wave ----
		WaveTable test_wave;
		
		
		
	private:

		
		

	
};

#endif
