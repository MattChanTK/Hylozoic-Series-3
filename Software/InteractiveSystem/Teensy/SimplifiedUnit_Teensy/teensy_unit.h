#ifndef _TEENSY_UNIT_H
#define _TEENSY_UNIT_H

#include "Arduino.h"


class TeensyUnit{
	
	public:
	
		//===============================================
		//==== pin assignments ====
		//===============================================
		
		//--- Teensy on-board ---
		const unsigned short indicator_led_pin = 13;
		const unsigned short analog_0_pin = A0;
		
		//--- Protocell module ---
		const unsigned short high_power_led_pin = 23;
		const unsigned short ambient_light_sensor_pin = A3;

		//--- Tentacle module ----
		const unsigned short sma_0_pin = 5;
		const unsigned short sma_1_pin = 6;
		const unsigned short reflex_0_pin = 9;
		const unsigned short reflex_1_pin = 10;
		const unsigned short ir_0_pin = A2;
		const unsigned short ir_1_pin = A1;
		const unsigned short acc_scl_pin = A5;
		const unsigned short acc_sda_pin = A4;

		//--- Sound module ---
		const unsigned short sound_detect_pin = 5;
		const unsigned short sound_trigger_pin = 6;
		const unsigned short sound_module_led_0_pin = 9;
		const unsigned short sound_module_led_1_pin = 10;
		const unsigned short sound_module_ir_pin = A2;
		const unsigned short vbatt_pin = A1;
		
		
		//===============================================
		//==== BEHAVIOUR variables =====
		//===============================================
		
		//--- Input Sampling ----
		//~~Teensy on-board~~
		volatile unsigned int analog_0_state = 0;
		//~~IR sensors state~~
		volatile unsigned int ir_0_state = 0;
		volatile unsigned int ir_1_state = 0;
		//~~Ambient light sensor state~~
		volatile unsigned int ambient_light_sensor_state = 0;
		//~~Sound module states~~
		volatile bool sound_detect_state = 0;
		volatile unsigned int sound_module_ir_state = 0;
		
		
		//---- indicator LED blinking -----
		//~~indicator LED on~~
		volatile bool indicator_led_on = true; //exposed
		//~~indicator LED blink~~
		volatile int indicator_led_blink_period = 5000; //exposed
				
		//----- Protocell reflex -----
		//~~output~~
		volatile unsigned short high_power_led_level = 0;  //exposed
		volatile int high_power_led_reflex_enabled = false;
		unsigned short high_power_led_level_max = 125;
		volatile unsigned int high_power_led_reflex_threshold = 50;
		
		//--- Tentacle reflex ----
		//~~output~~
		volatile boolean tentacle_reflex_enabled = true;
		volatile unsigned short sma_0_level = 0; //exposed
		volatile unsigned short sma_1_level = 0; //exposed
		volatile unsigned short reflex_0_level = 0; //exposed
		volatile unsigned short reflex_1_level = 0; //exposed
		volatile unsigned int ir_0_threshold = 150;
		volatile unsigned int ir_1_threshold = 150;
		
		//--- sound module reflex ---
		//~~output~~
		volatile boolean sound_module_reflex_enabled = true;
		
		
		//===============================================
		//==== Functions ====
		//===============================================
		
		//--- Constructor and destructor ---
		TeensyUnit();
		~TeensyUnit();
		
		// test function
		void set_led_state();
		
		//--- Initialization ---
		void init();
		
		//--- Communication functions ----
		bool receive_msg();
		void send_msg();
		void parse_msg();
		void compose_reply(byte front_signature, byte back_signature);
		
		//--- Input functions----
		void sample_inputs();
		
	private:
		
		//==== constants ====
		const unsigned int num_outgoing_byte = 64;
		const unsigned int num_incoming_byte = 64;
		

		//==== COMMUNICATION variables =====
		byte send_data_buff[64];
		byte recv_data_buff[64];

};


#endif
