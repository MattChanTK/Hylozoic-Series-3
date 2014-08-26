#ifndef _TEENSY_UNIT_H
#define _TEENSY_UNIT_H

#include "Arduino.h"


class TeensyUnit{
	
	public:
	
		//===============================================
		//==== pin assignments ====
		//===============================================
		
		//--- Teensy on-board ---
		const uint8_t indicator_led_pin = 13;
		const uint8_t analog_0_pin = A0;
		
		//--- Protocell module ---
		const uint8_t high_power_led_pin = 23;
		const uint8_t ambient_light_sensor_pin = A3;

		//--- Tentacle module ----
		const uint8_t sma_0_pin = 5;
		const uint8_t sma_1_pin = 6;
		const uint8_t reflex_0_pin = 9;
		const uint8_t reflex_1_pin = 10;
		const uint8_t ir_0_pin = A2;
		const uint8_t ir_1_pin = A1;
		const uint8_t acc_scl_pin = A5;
		const uint8_t acc_sda_pin = A4;

		//--- Sound module ---
		const uint8_t sound_detect_pin = 5;
		const uint8_t sound_trigger_pin = 6;
		const uint8_t sound_module_led_0_pin = 9;
		const uint8_t sound_module_led_1_pin = 10;
		const uint8_t sound_module_ir_pin = A2;
		const uint8_t vbatt_pin = A1;
		
		
		//===============================================
		//==== BEHAVIOUR variables =====
		//===============================================
		
		//--- Input Sampling ----
		//~~Teensy on-board~~
		uint16_t analog_0_state = 0;
		//~~IR sensors state~~
		uint16_t ir_0_state = 0;
		uint16_t ir_1_state = 0;
		//~~Ambient light sensor state~~
		uint16_t ambient_light_sensor_state = 0;
		//~~Sound module states~~
		bool sound_detect_state = 0;
		uint16_t sound_module_ir_state = 0;
		
		
		//---- indicator LED blinking -----
		//~~indicator LED on~~
		bool indicator_led_on = true; //exposed
		//~~indicator LED blink~~
		int16_t indicator_led_blink_period = 5000; //exposed
				
		//----- Protocell reflex -----
		//~~output~~
		uint8_t high_power_led_level = 0;  //exposed
		bool high_power_led_reflex_enabled = false;
		uint8_t high_power_led_level_max = 125;
		uint16_t high_power_led_reflex_threshold = 50;
		
		//--- Tentacle reflex ----
		//~~output~~
		bool tentacle_reflex_enabled = true;
		uint8_t sma_0_level = 0; //exposed
		uint8_t sma_1_level = 0; //exposed
		uint8_t reflex_0_level = 0; //exposed
		uint8_t reflex_1_level = 0; //exposed
		uint16_t ir_0_threshold = 150;
		uint16_t ir_1_threshold = 150;
		
		//--- sound module reflex ---
		//~~output~~
		boolean sound_module_reflex_enabled = true;
		
		
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
		const uint16_t num_outgoing_byte = 64;
		const uint16_t num_incoming_byte = 64;
		

		//==== COMMUNICATION variables =====
		byte send_data_buff[64];
		byte recv_data_buff[64];

};


#endif
