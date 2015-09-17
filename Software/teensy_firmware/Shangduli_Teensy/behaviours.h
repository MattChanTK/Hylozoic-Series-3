#ifndef _BEHAVIOUR_H
#define _BEHAVIOUR_H

#include "Arduino.h"
#include "teensy_unit.h"

#define NUM_WAVE 10


class FinVar{

	private:
	
		friend class Behaviours;
	
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

class LightVar{

	private:
	
		friend class Behaviours;
		
		//----INPUT----
		
		//~~Ambient light sensor state~~
		uint16_t als_state = 0;
		
		
		//----OUTPUT (internal variables)----
		
		//~~Ambient light sensor thresholds
		uint16_t als_threshold = 100;
		
		//~~high-power LED cycle period
		uint16_t cycle_period = 3000;
		
		//----OUTPUT (actuators)----
		
		//~~high-power LED level~~~		
		uint8_t led_level = 5;

		//~~high-power LED waveform type~~
		uint8_t led_wave_type = 0;
				
	

};

class SoundVar{
	
	private:
	
		friend class Behaviours;
		
		//----INPUT----
		
		//~~din states~~
		uint16_t din_state[2] = {0, 0};
		
		
		//----OUTPUT (internal variables)----
		
		
		//----OUTPUT (actuators)----
		
		//~~trigger states~~~		
		uint8_t trig_state[2] = {255, 255};
		
		//~~behaviour variable~~
		int16_t play_delay = 0;
		uint32_t phase_time = 0;
		uint8_t play_type = 0;
		uint16_t prev_din = 4095;
		int8_t play_activity = 0;
				
	
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
		void low_level_control_sound_behaviour();
		
		//---- self-running behaviour ---
		void sound_neighbourhood_behaviour(const uint32_t &curr_time);
		
		//===============================================
		//==== BEHAVIOUR variables =====
		//===============================================
		
	
		
		
		//>>> Teensy on-board <<<<
		
		//----OUTPUT----
		//~~indicator LED on~~
		bool indicator_led_on = 1; 
		//~~indicator LED blink~~
		uint16_t indicator_led_blink_period = 1000; 
		
		
		//~~operation mode~~~
		uint8_t operation_mode = 0;
		
		//>> Sound <<
		SoundVar sound_var[NUM_SOUND];
		
		
		//>>> Network Activities <<<
		uint8_t sound_spatial_arr[NUM_SOUND] = {0, 1, 2, 3, 4, 5};
		
		//----OUTPUT (internal variables)----
		uint8_t neighbour_activation_state = 0;	

	
};


#endif
