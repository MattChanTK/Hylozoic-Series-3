#ifndef _RAWHID_COMMUNICATOR_H
#define _RAWHID_COMMUNICATOR_H


#include "wave_table.h"
#include "i2c_t3.h"
#include "PWMDriver.h"
#include "Arduino.h"

#define PACKET_SIZE 64
#define I2C_TIMEOUT 1000 //microsecond


class RawHIDCommunicator{
		
	public:
	
		void init();
		
		//--- Communication functions ----
		bool receive_msg();
		void send_msg();
		uint8_t get_msg_setting();
		virtual void parse_msg() = 0;
		virtual void compose_reply(byte front_signature, byte back_signature, byte msg_setting) = 0;
		
	protected:
		
		//==== constants ====
		const uint8_t num_outgoing_byte = PACKET_SIZE;
		const uint8_t num_incoming_byte = PACKET_SIZE;
		
		//==== COMMUNICATION variables =====
		byte send_data_buff[PACKET_SIZE];
		byte recv_data_buff[PACKET_SIZE];
		uint8_t request_type = 0;
		uint8_t reply_type = 0;
		uint8_t msg_setting = 0;
};
		
#endif