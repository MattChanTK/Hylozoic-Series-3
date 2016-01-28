#ifndef _RAWHID_COMMUNICATOR_H
#define _RAWHID_COMMUNICATOR_H


#include "wave_table.h"
#include "i2c_t3.h"
#include "PWMDriver.h"
#include "Arduino.h"

#define PACKET_SIZE 64
#define I2C_TIMEOUT 1000 //microsecond

enum RequestType {
	Basic,
	Reset,
	LowLevel,
	MidLevel,
	ReadOnly=255
};

enum ResponseType {
	Readings,
	Echo
};

class RawHIDCommunicator{
		
	public:
	
		void init();
		
		//--- Communication functions ----
		bool receive_msg();
		void send_msg();
		uint8_t get_msg_setting();
		virtual void parse_msg() = 0;
		virtual void compose_reply(byte front_signature, byte back_signature, byte msg_setting) = 0;
		
		
		//>>> Teensy on-board <<<<
		
		//----OUTPUT----
		//~~indicator LED on~~
		bool indicator_led_on = false; 
		//~~indicator LED blink~~
		uint16_t indicator_led_blink_period = 1000; 
		
		//~~operation mode~~~
		uint8_t operation_mode = 0;
		
		//>>> Network Activities <<<
		
		//----OUTPUT (internal variables)----
		uint8_t neighbour_activation_state = 0;
		
	protected:
		
		//==== constants ====
		const uint8_t num_outgoing_byte = PACKET_SIZE;
		const uint8_t num_incoming_byte = PACKET_SIZE;
		
		//==== COMMUNICATION variables =====
		byte send_data_buff[PACKET_SIZE];
		byte recv_data_buff[PACKET_SIZE];
		RequestType request_type = Basic;
		ResponseType reply_type = Readings;
		uint8_t msg_setting = 0;
		
		/*! Get a 16-bit integer back from the transmission
		*/
		uint16_t getInt16(uint8_t offset);
};
		
#endif