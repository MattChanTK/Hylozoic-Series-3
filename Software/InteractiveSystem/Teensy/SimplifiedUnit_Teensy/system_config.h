#ifndef _SYSTEM_CONFIG_H
#define _SYSTEM_CONFIG_H

#include "Arduino.h"


class TeensyUnit{

	
	public:
		TeensyUnit();
		void init();
		void set_led_state(bool state);
		boolean receive_msg();
		void send_msg();
		void parse_msg(byte data_buff[]);
		void compose_reply(byte data_buff[], byte front_signature, byte back_signature);

		
	private:
		//==== pin assignments ====
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

		
		//==== constants ====
		const unsigned int num_outgoing_byte = 64;
		const unsigned int num_incoming_byte = 64;
		

		//==== internal variables =====
		byte send_data_buff[64];
		byte recv_data_buff[64];
		unsigned long msUntilNextSend = millis() + period;
		unsigned int packetCount = 0;
		volatile boolean ledState = 1;
		const unsigned int period = 0;

};


#endif
