#ifndef _CRICKET_H
#define _CRICKET_H

/*#include "Arduino.h"
#include "fins_crickets_unit.h"
#include "fins_lights_unit.h"
#include "sounds_unit.h"

#include <Statistic.h>*/

// External Includes
#include "crickets_lights_unit.h"

// Internal Includes
#include "light.h"

class CricketUnitVar{

	private:
	
		friend class WashingtonCricketNode;
		friend class WashingtonFinCricketNode;
	
		//----INPUT----
		uint16_t ir_state = 0;
		
		//----OUTPUT (internal variables)----
		uint32_t phase_time = 0;
		uint32_t step_time = 0;
		bool cycling = false;
		uint32_t next_step_time = 0;
		
		//----OUTPUT (actuators)----
		
		//~~individual PWM level~~~		
		// 4 Cricket Chains per Cricket Unit
		uint8_t output_level[4] = {0, 0, 0, 0};
		
		

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
		
		//---- self-running behaviour ----
		void self_running_behaviour(const uint32_t &curr_time);
		
		//---- indicator LED -----
		void led_blink_behaviour(const uint32_t &curr_time);
	
		//---- low-level control ---
		void low_level_control_behaviour(const uint32_t &curr_time);

		
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
		CricketUnitVar cricket_var[WashingtonCricketNode::NUM_CRICKET];
		
		//>>> Lightt <<<
		LightUnitVar light_var[WashingtonCricketNode::NUM_LIGHT];
				
		
		//>>> Network Activities <<<
		
		//----OUTPUT (internal variables)----
		uint8_t neighbour_activation_state = 0;
		
	
	private:

		

	
};


#endif
