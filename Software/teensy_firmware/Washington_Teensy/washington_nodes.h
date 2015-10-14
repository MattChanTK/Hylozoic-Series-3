#ifndef _WASHINGTON_NODES_H
#define _WASHINGTON_NODES_H

#include "Arduino.h"
#include "crickets_unit.h"


class CricketVar{

	private:
	
		friend class WashingtonCricketsUnit;
	
		//----INPUT----
			
		
		//----OUTPUT (internal variables)----
		
		
		//----OUTPUT (actuators)----
		
		//~~individual SMA PWM level~~~		
		// 4 Cricket Chains per Cricket Unit
		uint8_t sma_level[4] = {0, 0, 0, 0};

};


class WashingtonCricketsUnit : public CricketsUnit{

	public:
		
		//===============================================
		//==== Constructor and destructor =====
		//===============================================
		
		WashingtonCricketsUnit();
		~WashingtonCricketsUnit();

		//===============================================
		//==== Communication functions =====
		//===============================================
			
		void parse_msg();
		void compose_reply(byte front_signature, byte back_signature, byte msg_setting);
		
		//--- Input functions----
		void sample_inputs();
		void sample_inputs(const uint8_t setting);
		
		//===============================================
		//==== BEHAVIOUR functions =====
		//===============================================
		
		//---- inactive behaviour ----
		void inactive_behaviour();
		
		//---- test behaviour ----
		void test_behaviour(const uint32_t &curr_time);
		
		//---- indicator LED -----
		void led_blink_behaviour(const uint32_t &curr_time);
	
		//---- low-level control ---
		void low_level_control_behaviour();

		
		//===============================================
		//==== BEHAVIOUR variables =====
		//===============================================	
		
		//>>> Teensy on-board <<<<
		
		//----OUTPUT----
		//~~indicator LED on~~
		bool indicator_led_on = false; 
		//~~indicator LED blink~~
		uint16_t indicator_led_blink_period = 1000; 
		
		//~~operation mode~~~
		uint8_t operation_mode = 0;

		//>>> Cricket <<<
		CricketVar cricket_var[NUM_CRICKET];
				
		
		//>>> Network Activities <<<
		
		//----OUTPUT (internal variables)----
		uint8_t neighbour_activation_state = 0;
		
	
	private:

		

	
};


#endif
