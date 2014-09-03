#ifndef _TEENSY_UNIT_H
#define _TEENSY_UNIT_H

#include "Arduino.h"
#include "wave_table.h"
#include "i2c_t3.h"

#define packet_size 64

class TeensyUnit{
	
	public:
	
		//===============================================
		//==== pin assignments ====
		//===============================================
		
		//--- Teensy on-board ---
		const uint8_t indicator_led_pin = 13;
		
		//--- Programming Pin ---
		const uint8_t PGM_DO_pin = 7;
		
		//--- FPWM pins ---
		//{FPWM_1_1, FPWM_1_2, FPWM_2_1, FPWM_2_2, FPWM_4_1, FPWM_4_2, FPWM_5_1, FPWWM_5_2}
		const uint8_t FPWM_pin[8] = {3, 4, 6, 5, 20, 21, 25, 21};
		
		//--- Analogue pins ---
		//{Analog_1_1, Analog_1_2, Analog_2_1, Analog_2_2, Analog_3_1, Analog_3_2, 
		// Analog_4_1, Analog_4_2, Analog_5_1, Analog_5_2, Analog_6_1, Analog_6_2}
		const uint8_t Analog_pin[12] = {A11, A13, A12, A15, A16, A17, A8, A9, A2, A3, A0, A1};
		
		//--- Multiplexer pins ---
		const uint8_t MUL_ADR_pin[3] = {2, 24, 33};
		
		//--- UART pins ---
		const uint8_t RX1_pin = 0;  //not being used
		const uint8_t TX1_pin = 1;  //not being used
		
		//--- SPI pins ---
		const uint8_t CE = 9;		//not being used
		const uint8_t CSN = 10;		//not being used
		const uint8_t MOSI = 11;	//not being used
		const uint8_t MISO = 12;	//not being used
		const uint8_t SCK = 13;		//not being used
		
		
		//===============================================
		//==== Ports ====
		//===============================================
		
		
		
		
		//===============================================
		//==== Functions ====
		//===============================================
		
		//--- Constructor and destructor ---
		TeensyUnit();
		~TeensyUnit();

		//--- Initialization ---
		void init();
		
		//--- Communication functions ----
		bool receive_msg();
		void send_msg();
		virtual void parse_msg() = 0;
		virtual void compose_reply(byte front_signature, byte back_signature) = 0;
		
		
		
	protected:
		
		//==== constants ====
		const uint8_t num_outgoing_byte = packet_size;
		const uint8_t num_incoming_byte = packet_size;

		
		//==== COMMUNICATION variables =====
		byte send_data_buff[packet_size];
		byte recv_data_buff[packet_size];
		uint8_t request_type = 0;
		
		//==== Port Classes ====
		
		//--- Tentacle ---
		class TentaclePort{
		
			public:

				//~~outputs~~
				bool port_enabled = true;
				uint8_t sma_level[2] = {0, 0}; 
				uint8_t led_level[2] = {0, 0}; 
				
				//~~inputs~~
				uint16_t analog_state[2];  //{IR 0, IR 1}
				uint16_t acc_state[3];  // {x, y, z}
				
			private:
			
				
			
		};
	
};


#endif
