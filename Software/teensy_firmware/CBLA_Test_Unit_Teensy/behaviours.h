#ifndef _BEHAVIOUR_H
#define _BEHAVIOUR_H

#include "Arduino.h"
#include "teensy_unit.h"

#define num_wave 10

class TentacleVar{

	private:
	
		friend class Behaviours;
	
		//----INPUT----
		
		//~~IR sensors state~~
		uint16_t tentacle_ir_state[2] = {0, 0};
		
		
		//~~Accelerometer~~
		// {x,y,z}
		int16_t tentacle_acc_state[3] = {0, 0, 0};
		
		
		//----internal behaviour variables----
		uint32_t tentacle_sensor_waveform_phase_time = 0;
		bool tentacle_sensor_waveform_cycling = 0;
		
		//~~Tentacle cycling~~
		uint8_t tentacle_cycling = 0;
		
		
		//----OUTPUT (internal variables)----
		
		//~~IR sensors activation threshold~~
		// {bottom IR, tip IR}
		uint16_t tentacle_ir_threshold[2] = {1400, 1400};

		
		//~~~ON and OFF periods of the Tentacle arm activation here~~~
		// {on time, off time} (in second)
		uint8_t tentacle_arm_cycle_period[2] = {2, 10};

		
		//~~~Period of the reflex LED~~~
		// {channel 1, channel 2} (in millisecond)
		uint16_t tentacle_reflex_period[2] = {5000, 100};

		
		//----OUTPUT (actuators)----
		
		//~~individual SMA PWM level~~~		
		// 2 SMA wires per Tentacle
		uint8_t tentacle_sma_level[2] = {0, 0};

		//~~Tentacle motion activation~~
		uint8_t tentacle_motion_on = 3;
	
		//~~Reflex actuation level~~
		// {channel 1, channel 2}
		uint8_t tentacle_reflex_level[2] = {0, 0};
	
		//~~Reflex wave type~~
		// {channel 1, channel 2}
		uint8_t tentacle_reflex_wave_type[2] =  {0, 1};

};

class ProtocellVar{

	private:
	
		friend class Behaviours;
		
		//----INPUT----
		
		//~~Ambient light sensor state~~
		uint16_t protocell_als_state = 0;
		
		
		//----OUTPUT (internal variables)----
		
		//~~Ambient light sensor thresholds
		uint16_t protocell_als_threshold = 100;
		
		//~~high-power LED cycle period
		uint16_t protocell_cycle_period = 3000;
		
		//----OUTPUT (actuators)----
		
		//~~high-power LED level~~~		
		uint8_t protocell_led_level = 5;

		//~~high-power LED waveform type~~
		uint8_t protocell_led_wave_type = 0;
				
	

};

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
		void compose_reply(byte front_signature, byte back_signature, byte msg_setting);
		
		//--- Input functions----
		void sample_inputs();
		void sample_inputs(const uint8_t setting);
		void sample_tentacle_sensor_waveform(const uint32_t &curr_time);
		
		//===============================================
		//==== BEHAVIOUR functions =====
		//===============================================
		
		//---- test behaviour ----
		void test_behaviour(const uint32_t &curr_time);
		void reflex_test_behaviour();
		void tentacle_arm_test_behaviour(const uint32_t &curr_time);
		
		//---- indicator LED -----
		void led_blink_behaviour(const uint32_t &curr_time);
		void led_wave_behaviour(const uint32_t &curr_time);
		
		//---- low-level control ---
		void low_level_control_tentacle_behaviour();
		void low_level_control_tentacle_reflex_led_behaviour();
		void low_level_control_protocell_behaviour();
		
		//---- high-level pre-programmed control ---
		void high_level_control_tentacle_reflex_behaviour(const uint32_t &curr_time);
		
		//---- high-level direct control ---
		void high_level_direct_control_tentacle_arm_behaviour(const uint32_t &curr_time);
		void high_level_direct_control_tentacle_arm_behaviour_continuous(const uint32_t &curr_time);


		
		//===============================================
		//==== BEHAVIOUR variables =====
		//===============================================
		
	
		//>>> Sensor Input Wave Form <<<<
		

		
		
		//>>> Teensy on-board <<<<
		
		//----OUTPUT----
		//~~indicator LED on~~
		bool indicator_led_on = false; //exposed
		//~~indicator LED blink~~
		uint16_t indicator_led_blink_period = 1000; //exposed
	
		//~~operation mode~~~
		uint8_t operation_mode = 0;

		//>>> Tentacle <<<
		TentacleVar tentacle_var[4];
		
		//>>> Protocell <<
		ProtocellVar protocell_var[2];
		
		
		//>>> Network Activities <<<
		
		//----OUTPUT (internal variables)----
		uint8_t neighbour_activation_state = 0;
		
		//>>> Wave Forms <<<
		
		//~~ instances ~~~
		WaveTable wave[num_wave];
		
		
		//~~ waveform definitions ~~~
		// const_wave_t cos_wave_1[wave_size] = {0, 2, 9, 21, 37, 56, 78, 102, 127, 151, 175, 197, 216, 232, 244, 251, 254, 251, 244, 232, 216, 197, 175, 151, 127, 102, 78, 56, 37, 21, 9, 2};
		// const_wave_t cos_wave_2[wave_size] = {126, 102, 78, 56, 37, 21, 9, 2, 0, 2, 9, 21, 37, 56, 78, 102, 127, 151, 175, 197, 216, 232, 244, 251, 254, 251, 244, 232, 216, 197, 175, 151};
		// const_wave_t cos_wave_3[wave_size] = {254, 251, 244, 232, 216, 197, 175, 151, 126, 102, 78, 56, 37, 21, 9, 2, 0, 2, 9, 21, 37, 56, 78, 102, 127, 151, 175, 197, 216, 232, 244, 251};
		// const_wave_t cos_wave_4[wave_size] = {127, 151, 175, 197, 216, 232, 244, 251, 254, 251, 244, 232, 216, 197, 175, 151, 126, 102, 78, 56, 37, 21, 9, 2, 0, 2, 9, 21, 37, 56, 78, 102};
	
		// const_wave_t reflex_cos_wave_1[wave_size] = {0, 0, 3, 7, 13, 22, 34, 49, 68, 92, 119, 149, 180, 209, 233, 249, 255, 249, 233, 209, 180, 149, 119, 92, 68, 49, 34, 22, 13, 7, 3, 0};
		// const_wave_t reflex_cos_wave_2[wave_size] = {68, 49, 34, 22, 13, 7, 3, 0, 0, 0, 3, 7, 13, 22, 34, 49, 68, 92, 119, 149, 180, 209, 233, 249, 255, 249, 233, 209, 180, 149, 119, 92};
		// const_wave_t reflex_cos_wave_3[wave_size] = {255, 249, 233, 209, 180, 149, 119, 92, 68, 49, 34, 22, 13, 7, 3, 0, 0, 0, 3, 7, 13, 22, 34, 49, 68, 92, 119, 149, 180, 209, 233, 249};
		// const_wave_t reflex_cos_wave_4[wave_size] = {68, 92, 119, 149, 180, 209, 233, 249, 255, 249, 233, 209, 180, 149, 119, 92, 68, 49, 34, 22, 13, 7, 3, 0, 0, 0, 3, 7, 13, 22, 34, 49};
		
		// const_wave_t cos_wave_1[wave_size] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 20, 51, 84, 115, 140, 157, 163, 157, 140, 115, 84, 51, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0};
		// const_wave_t cos_wave_2[wave_size] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 20, 51, 84, 115, 140, 157, 163, 157, 140, 115, 84, 51, 20, 0, 0, 0, 0, 0};
		// const_wave_t cos_wave_3[wave_size] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 20, 51, 84, 115, 140, 157, 163, 157, 140, 115, 84, 51, 20, 0};
		// const_wave_t cos_wave_4[wave_size] = {84, 51, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 20, 51, 84, 115, 140, 157, 163, 157, 140, 115};
		
	
	private:

		

	
};


#endif
