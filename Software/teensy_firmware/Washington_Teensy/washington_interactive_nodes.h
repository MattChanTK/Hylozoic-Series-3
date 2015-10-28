#ifndef _WASHINGTON_INTERACTIVE_NODES_H
#define _WASHINGTON_INTERACTIVE_NODES_H

#include "Arduino.h"
#include "crickets_lights_unit.h"
#include "fins_crickets_unit.h"
#include "fins_lights_unit.h"
#include "sounds_unit.h"


class CricketUnitVar{

	private:
	
		friend class WashingtonCricketNode;
		friend class WashingtonFinCricketNode;
	
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
		friend class WashingtonFinNode;
	
		//----INPUT----
		uint16_t ir_state[2] = {0, 0};
		
		//----OUTPUT (internal variables)----
		
		
		//----OUTPUT (actuators)----
		
		//~~individual PWM level~~~		
		// 4 LED Chains per Light Unit
		uint8_t led_level[4] = {0, 0, 0, 0};
		

};



class FinUnitVar{

	private:
	
		friend class WashingtonFinCricketNode;
		friend class WashingtonFinNode;
	
		//----INPUT----
		
		//~~IR sensors state~~
		uint16_t ir_state[2] = {0, 0};
		
		
		//~~Accelerometer~~
		// {x,y,z}
		int16_t acc_state[3] = {0, 0, 0};
		
		
		//----internal behaviour variables----
		uint32_t sensor_waveform_phase_time = 0;
		bool sensor_waveform_cycling = 0;
		
		//~~Fin cycling~~
		uint8_t cycling = 0;
		
		
		//----OUTPUT (internal variables)----
		
		//~~IR sensors activation threshold~~
		// {bottom IR, tip IR}
		uint16_t ir_threshold[2] = {1400, 1400};

		
		//~~~ON and OFF periods of the Fin arm activation here~~~
		// {on time, off time} (in 0.1 second)
		uint8_t arm_cycle_period[2] = {20, 100};

		
		//~~~Period of the reflex LED~~~
		// {channel 1, channel 2} (in millisecond)
		uint16_t reflex_period[2] = {5000, 100};

		
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

class SoundUnitVar{

	private:
	
		friend class WashingtonSoundNode;
	
		//----INPUT----
		
		//~~Analog state~~
		uint16_t analog_state[3] = {0, 0, 0};
		
	
		//----OUTPUT----
		
		bool digital_trigger[2] = {0, 0};
		uint8_t output_level[2] = {0, 0};
		
		uint8_t sound_type[2] = {0, 0}; // 0 = off
		uint8_t sound_volume[2] = {0, 0}; // 0 = 0%, 50 = 100%, 100 = 200%
		uint8_t sound_block[2] = {0, 0};
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
		CricketUnitVar cricket_var[WashingtonCricketNode::NUM_CRICKET];
		
		//>>> Lightt <<<
		LightUnitVar light_var[WashingtonCricketNode::NUM_LIGHT];
				
		
		//>>> Network Activities <<<
		
		//----OUTPUT (internal variables)----
		uint8_t neighbour_activation_state = 0;
		
	
	private:

		

	
};

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
		CricketUnitVar cricket_var[WashingtonFinCricketNode::NUM_CRICKET];
		
		//>>> Fin <<<
		FinUnitVar fin_var[WashingtonFinCricketNode::NUM_FIN];
				
		
		//>>> Network Activities <<<
		
		//----OUTPUT (internal variables)----
		uint8_t neighbour_activation_state = 0;
		
	
	private:

		

	
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

	
		//>>> Fin <<<
		FinUnitVar fin_var[WashingtonFinNode::NUM_FIN];
		
		//>>> Light <<<
		LightUnitVar light_var[WashingtonFinNode::NUM_LIGHT];
		
				
		
		//>>> Network Activities <<<
		
		//----OUTPUT (internal variables)----
		uint8_t neighbour_activation_state = 0;
		
	
	private:

		

	
};

class WashingtonSoundNode : public SoundsUnit{

	public:
		
		//===============================================
		//==== Constructor and destructor =====
		//===============================================
		
		WashingtonSoundNode(uint8_t sound0_port_id, 
							uint8_t sound1_port_id, 
							uint8_t sound2_port_id,
							uint8_t sound3_port_id, 
							uint8_t sound4_port_id, 
							uint8_t sound5_port_id
						    );
		~WashingtonSoundNode();

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

		//>>> Sound <<<
		SoundUnitVar sound_var[WashingtonSoundNode::NUM_SOUND];
		// bool play_started_L[4] = {false, false, false, false};
		// bool play_started_R[4] = {false, false, false, false};
		
		//>>> Network Activities <<<
		
		//----OUTPUT (internal variables)----
		uint8_t neighbour_activation_state = 0;
		
	
	private:

		

	
};



#endif
