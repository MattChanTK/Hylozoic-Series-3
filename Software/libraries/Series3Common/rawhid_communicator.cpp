#include "rawhid_communicator.h"


void RawHIDCommunicator::init(){
	
	unsigned long clearing_counter = 0;
	while (receive_msg()){
	    // this prevents the Teensy from being stuck in infinite loop
	    clearing_counter++;
	    if (clearing_counter>10){
			break;
        }
		
	}
	
}

//===========================================================================
//====== COMMUNICATION ======
//===========================================================================

bool RawHIDCommunicator::receive_msg(){

	noInterrupts();
	uint8_t byteCount = 0;
	byteCount = RawHID.recv(recv_data_buff, 0);
	interrupts();

	if (byteCount > 0) {
		
		
		// extract the front and end signatures
		byte front_signature = recv_data_buff[0];
		byte back_signature = recv_data_buff[num_incoming_byte-1];
		
		// check if it's a write-only message
		byte msg_setting = recv_data_buff[num_incoming_byte-2];

		// compose reply message
		this->compose_reply(front_signature, back_signature, msg_setting);
		send_msg();


		return true;
	}
	else{

		return false;
	}
}

void RawHIDCommunicator::send_msg(){

	// Send a message
	noInterrupts();
	RawHID.send(send_data_buff, 10);
	interrupts();
}

uint8_t RawHIDCommunicator::get_msg_setting(){

	return msg_setting;


}