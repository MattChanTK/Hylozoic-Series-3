#ifndef _WASHINGTON_INTERACTIVE_NODES_H
#define _WASHINGTON_INTERACTIVE_NODES_H

#include "Arduino.h"
#include "crickets_lights_unit.h"


class CricketUnitVar{

	private:
	
		friend class WashingtonCricketNode;
	
		//----INPUT----
		uint16_t ir_state = 0;
		
		//----OUTPUT (internal variables)----
		
		
		//----OUTPUT (actuators)----
		
		//~~individual PWM level~~~		
		// 4 Cricket Chains per Cricket Unit
		uint8_t output_level[4] = {0, 0, 0, 0};
		
		

};

class LightUnitVar{

	private:
	
		friend class WashingtonCricketNode;
	
		//----INPUT----
		uint16_t ir_state[2] = {0, 0};
		
		//----OUTPUT (internal variables)----
		
		
		//----OUTPUT (actuators)----
		
		//~~individual PWM level~~~		
		// 4 LED Chains per Light Unit
		uint8_t led_level[4] = {0, 0, 0, 0};
		
		
		

};



class WashingtonCricketNode : public CricketsLightsUnit{

	public:
		
		//===============================================
		//==== Constructor and destructor =====
		//===============================================
		
		WashingtonCricketNode(uint8_t cricket0_port_id, 
							   uint8_t cricket1_port_id, 
							   uint8_t cricket2_port_id,
							   uint8_t light0_port_id
							   );
		~WashingtonCricketNode();

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
		CricketUnitVar cricket_var[NUM_CRICKET];
		
		//>>> Lightt <<<
		LightUnitVar light_var[NUM_LIGHT];
				
		
		//>>> Network Activities <<<
		
		//----OUTPUT (internal variables)----
		uint8_t neighbour_activation_state = 0;
		
	
	private:

		

	
};


#endif
