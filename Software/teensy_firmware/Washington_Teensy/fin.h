#ifndef _FIN_H
#define _FIN_H

#include "Arduino.h"
#include "Statistic.h"

#include "fins_crickets_unit.h"
#include "fins_lights_unit.h"

#include "light.h"

class FinUnitVar{

	private:
	
		friend class WashingtonFinCricketNode;
		friend class WashingtonFinNode;
	
		//----INPUT----
		
		//~~IR sensors state~~
		uint16_t ir_state[2] = {0, 0};
    Statistic ir_averages[2];
		
		//~~Accelerometer~~
		// {x,y,z}
		int16_t acc_state[3] = {0, 0, 0};
		
		
		//----internal behaviour variables----
		uint32_t sensor_waveform_phase_time = 0;
		bool sensor_waveform_cycling = 0;
		
		//~~Fin cycling~~
		uint8_t cycling = 0; // What does this mean? DK
		
		//~~Reflex Light Cycling ~~
		bool reflex_cycling = false;
		uint32_t reflex_phase_time = millis();  	
		uint32_t reflex_step_time = millis();
		uint32_t reflex_next_step_time = 1;
		
		
		//----OUTPUT (internal variables)----
		
		//~~IR sensors activation threshold~~
		// {bottom IR, tip IR}
		uint16_t ir_threshold[2] = {1400, 1400};

		
		//~~~ON and OFF periods of the Fin arm activation here~~~
		// {on time, off time} (in 0.1 second)
		uint8_t arm_cycle_period[2] = {15, 100};

		
		//~~~Period of the reflex LED~~~
		// {channel 1, channel 2} (in millisecond)
		uint16_t reflex_period[2] = {5000, 100};
		
		//~~~Amount of time the SMAs were last on~~~
		// {channel 1, channel 2} (in millisecond)
		uint32_t sma_on_time[2] = {0, 0};
		
		//~~~Maximum SMA output level~~
		uint8_t sma_max_level[2] = {150, 150};

		
		//----OUTPUT (actuators)----
		
		//~~individual SMA PWM level~~~		
		// 2 SMA wires per Fin
		uint8_t sma_level[2] = {0, 0};

		//~~Fin motion activation~~
		uint8_t motion_on = 3;
	
		//~~Reflex actuation level~~
		// {channel 1, channel 2}
		uint8_t reflex_level[2] = {0, 0};
	
		//~~Reflex wave type~~
		// {channel 1, channel 2}
		uint8_t reflex_wave_type[2] =  {0, 1};

};

class WashingtonFinNode : public FinsLightsUnit{

	public:
		
		//===============================================
		//==== Constructor and destructor =====
		//===============================================
		
		WashingtonFinNode(uint8_t fin0_port_id, 
						  uint8_t fin1_port_id, 
						  uint8_t fin2_port_id,
						  uint8_t light0_port_id, 
						  uint8_t light1_port_id, 
						  uint8_t light2_port_id
					     );
		~WashingtonFinNode();

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

	
		//>>> Fin <<<
		FinUnitVar fin_var[WashingtonFinNode::NUM_FIN];
		
		//>>> Light <<<
		LightUnitVar light_var[WashingtonFinNode::NUM_LIGHT];
		
				
		
		//>>> Network Activities <<<
		
		//----OUTPUT (internal variables)----
		uint8_t neighbour_activation_state = 0;
		
	
	private:

		

	
};

#endif
