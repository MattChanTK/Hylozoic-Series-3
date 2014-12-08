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
		void stress_test_behaviour(const uint32_t &curr_time);
		
		//---- indicator LED -----
		void led_blink_behaviour(const uint32_t &curr_time);
		void led_wave_behaviour(const uint32_t &curr_time);
		
		//----- tentacle primary action -----
		void tentacle_tip_ir_primary_action(const uint32_t &curr_time);
		void tentacle_scout_ir_primary_action(const uint32_t &curr_time);
		
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
		
		
		//---- indicator LED blinking -----
		//~~indicator LED on~~
		bool indicator_led_on = true; //exposed
		//~~indicator LED blink~~
		int16_t indicator_led_blink_period = 5000; //exposed
				
		
		//>>>Tentacle<<<<
		
		//--- Tentacle tip primary action ----
		
		//~~input~~
		//*** edit the IR sensors' thresholds for the Tentacle (SMA) behaviours here ****
		// {bottom IR, tip IR}
		uint8_t tentacle_0_ir_threshold[2] = {50, 80};
		uint8_t tentacle_1_ir_threshold[2] = {50, 80};
		uint8_t tentacle_2_ir_threshold[2] = {50, 80};
		uint8_t* tentacle_ir_threshold[3];
		
		//~~output~~
		//*** edit the ON and OFF periods of an SMA activation here ****
		// {on time, off time}
		uint8_t tentacle_0_cycle_period[2] = {2, 15};
		uint8_t tentacle_1_cycle_period[2] = {2, 15};
		uint8_t tentacle_2_cycle_period[2] = {2, 15};
		uint8_t* tentacle_cycle_period[3];
		
		// {tentacle 0, tentacle 1, tentacle 2} in ms
		uint16_t tentacle_cycle_offset[3] = {1000, 1000, 1000};
		
		
		//--- Tentacle scout primary action ----
		
		//~~input~~
		int8_t period_change_rate = 10;
		
		//*** edit the triggering threshold of bottom IR sensors for reflex and extra lights behaviours****
		//{far, close, very close}
		uint8_t tentacle_0_scout_ir_threshold[3] = {40, 80, 120};
		uint8_t tentacle_1_scout_ir_threshold[3] = {40, 80, 120};
		uint8_t tentacle_2_scout_ir_threshold[3] = {40, 80, 120};
		uint8_t* tentacle_scout_ir_threshold[3];
		
		//~~output~~		
		//*** edit the periods of the waveform of the reflex LED here****
		//three distances: {far, close, very close}
		uint16_t preset_scout_led_0_period[3] = {5000, 5000, 1000};
		uint16_t preset_scout_led_1_period[3] = {5000, 5000, 1000};
		uint16_t preset_scout_led_2_period[3] = {5000, 5000, 1000};
		uint16_t* preset_scout_led_period[3];
		
		//*** edit the periods of the waveform of the high-power LED here****
		
		// wave forms
		// const_wave_t cos_wave_1[wave_size] = {0, 2, 9, 21, 37, 56, 78, 102, 127, 151, 175, 197, 216, 232, 244, 251, 254, 251, 244, 232, 216, 197, 175, 151, 127, 102, 78, 56, 37, 21, 9, 2};
		// const_wave_t cos_wave_2[wave_size] = {126, 102, 78, 56, 37, 21, 9, 2, 0, 2, 9, 21, 37, 56, 78, 102, 127, 151, 175, 197, 216, 232, 244, 251, 254, 251, 244, 232, 216, 197, 175, 151};
		// const_wave_t cos_wave_3[wave_size] = {254, 251, 244, 232, 216, 197, 175, 151, 126, 102, 78, 56, 37, 21, 9, 2, 0, 2, 9, 21, 37, 56, 78, 102, 127, 151, 175, 197, 216, 232, 244, 251};
		// const_wave_t cos_wave_4[wave_size] = {127, 151, 175, 197, 216, 232, 244, 251, 254, 251, 244, 232, 216, 197, 175, 151, 126, 102, 78, 56, 37, 21, 9, 2, 0, 2, 9, 21, 37, 56, 78, 102};
		
		//*** edit the waveform for the reflex LED here****
		const_wave_t reflex_cos_wave_1[wave_size] = {0, 0, 3, 7, 13, 22, 34, 49, 68, 92, 119, 149, 180, 209, 233, 249, 255, 249, 233, 209, 180, 149, 119, 92, 68, 49, 34, 22, 13, 7, 3, 0};
		// const_wave_t cos_wave_2[wave_size] = {68, 49, 34, 22, 13, 7, 3, 0, 0, 0, 3, 7, 13, 22, 34, 49, 68, 92, 119, 149, 180, 209, 233, 249, 255, 249, 233, 209, 180, 149, 119, 92};
		// const_wave_t cos_wave_3[wave_size] = {255, 249, 233, 209, 180, 149, 119, 92, 68, 49, 34, 22, 13, 7, 3, 0, 0, 0, 3, 7, 13, 22, 34, 49, 68, 92, 119, 149, 180, 209, 233, 249};
		// const_wave_t cos_wave_4[wave_size] = {68, 92, 119, 149, 180, 209, 233, 249, 255, 249, 233, 209, 180, 149, 119, 92, 68, 49, 34, 22, 13, 7, 3, 0, 0, 0, 3, 7, 13, 22, 34, 49};
		
		//*** edit the waveform for the four high-power LED here****
		const_wave_t cos_wave_1[wave_size] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 20, 51, 84, 115, 140, 157, 163, 157, 140, 115, 84, 51, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0};
		const_wave_t cos_wave_2[wave_size] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 20, 51, 84, 115, 140, 157, 163, 157, 140, 115, 84, 51, 20, 0, 0, 0, 0, 0};
		const_wave_t cos_wave_3[wave_size] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 20, 51, 84, 115, 140, 157, 163, 157, 140, 115, 84, 51, 20, 0};
		const_wave_t cos_wave_4[wave_size] = {84, 51, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 20, 51, 84, 115, 140, 157, 163, 157, 140, 115};
		
		
		WaveTable scout_led_0_wave;
		WaveTable scout_led_1_wave;
		WaveTable scout_led_2_wave;
		WaveTable scout_led_wave[3];

		WaveTable test_wave;
		
		
	private:

		

	
};

#endif
