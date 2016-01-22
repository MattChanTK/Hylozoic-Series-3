#ifndef _FIN_CRICKET_H
#define _FIN_CRICKET_H

#include "fin.h"
#include "cricket.h"
#include "fins_crickets_unit.h"

class WashingtonFinCricketNode : public FinsCricketsUnit{

	public:
		
		//===============================================
		//==== Constructor and destructor =====
		//===============================================
		
		WashingtonFinCricketNode(uint8_t fin0_port_id, 
								 uint8_t fin1_port_id, 
								 uint8_t fin2_port_id,
								 uint8_t cricket0_port_id, 
								 uint8_t cricket1_port_id, 
								 uint8_t cricket2_port_id
								);
		~WashingtonFinCricketNode();

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
		CricketUnitVar cricket_var[WashingtonFinCricketNode::NUM_CRICKET];
		
		//>>> Fin <<<
		FinUnitVar fin_var[WashingtonFinCricketNode::NUM_FIN];
				
		
		//>>> Network Activities <<<
		
		//----OUTPUT (internal variables)----
		uint8_t neighbour_activation_state = 0;
		
	
	private:

		

	
};

#endif
