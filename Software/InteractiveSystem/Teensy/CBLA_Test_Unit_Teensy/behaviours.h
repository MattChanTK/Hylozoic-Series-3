#ifndef _BEHAVIOUR_H
#define _BEHAVIOUR_H

#include "Arduino.h"
#include "teensy_unit.h"


class TentacleVar{

	private:
	
		friend class Behaviours;
	
		//----INPUT----
		
		//~~IR sensors state~~
		uint16_t tentacle_ir_state[2] = {0, 0};
		
		
		//~~Accelerometer~~
		// {x,y,z}
		uint16_t tentacle_acc_state[3] = {0, 0, 0};
		
		//----OUTPUT (internal variables)----
		
		//~~IR sensors activation threshold~~
		// {bottom IR, tip IR}
		uint16_t tentacle_ir_threshold[2] = {50, 80};

		
		//~~~ON and OFF periods of the Tentacle arm activation here~~~
		// {on time, off time} (in second)
		uint8_t tentacle_arm_cycle_period[2] = {2, 15};

		
		//~~~Period of the reflex LED~~~
		// {channel 1, channel 2} (in millisecond)
		uint16_t tentacle_reflex_period[2] = {5000, 100};

		
		//----OUTPUT (actuators)----
		
		//~~individual SMA PWM level~~~		
		// 2 SMA wires per Tentacle
		uint8_t tentacle_sma_level[2] = {0, 0};

		//~~Tentacle motion activation~~
		uint8_t tentacle_motion_on = 0;
	
		//~~Reflex actuation level~~
		// {channel 1, channel 2}
		uint8_t tentacle_reflex_level[2] = {0, 0};
	
		//~~Reflex wave type~~
		// {channel 1, channel 2}
		uint8_t tentacle_reflex_wave_type[2] =  {0, 0};

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
		uint8_t protocell_cycle_period = 3000;
		
		//----OUTPUT (actuators)----
		
		//~~high-power LED level~~~		
		uint8_t protocell_led_level = 0;

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
		

		
		//===============================================
		//==== BEHAVIOUR variables =====
		//===============================================
		
	
		//>>> Teensy on-board <<<<
		
		//----OUTPUT----
		//~~indicator LED on~~
		bool indicator_led_on = true; //exposed
		//~~indicator LED blink~~
		uint16_t indicator_led_blink_period = 5000; //exposed
	
		//~~operation mode~~~
		uint8_t operation_mode = 0;

		//>>> Tentacle <<<
		TentacleVar tentacle_var[4];
		
		//>>> Protocell <<
		ProtocellVar protocell_var[2];
		
		
		//>>> Network Activities <<<
		
		//----INPUT----
		uint8_t neighbour_activation_state = 0;
		
		//>>> Wave Forms <<<
		//~~ instances ~~~
		WaveTable test_wave;
		
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
