#include "teensy_unit.h"

//===========================================================================
//===== CONSTRUCTOR and DECONSTRUCTOR =====
//===========================================================================

TeensyUnit::TeensyUnit(){
	

	//===============================================
	//==== pin initialization ====
	//===============================================
	
	uint8_t num_pins = 0;
	
	//--- Teensy On-Board ---
	pinMode(indicator_led_pin, OUTPUT);

	//--- Programming Pin ---
	pinMode(PGM_DO_pin, OUTPUT);
	
	//--- FPWM pins ---
	num_pins = sizeof(FPWM_pin)/sizeof(FPWM_pin[0]);
	for (uint8_t i = 0; i<num_pins; i++){
		pinMode(FPWM_pin[i], OUTPUT);
	}
	
	//--- Analogue pins ---
	num_pins = sizeof(Analog_pin)/sizeof(Analog_pin[0]);
	for (uint8_t i = 0; i<num_pins; i++){
		pinMode(Analog_pin[i], INPUT);
	}	
	
	//--- Multiplexer pins ---
	num_pins = sizeof(MUL_ADR_pin)/sizeof(MUL_ADR_pin[0]);
	for (uint8_t i = 0; i<num_pins; i++){
		pinMode(MUL_ADR_pin[i], OUTPUT);
	}	
	
	
	
	
}

TeensyUnit::~TeensyUnit(){

}

//===========================================================================
//===== INITIALIZATION =====
//===========================================================================

void TeensyUnit::init(){

	//===== clear all existing messages ======
	unsigned long clearing_counter = 0;
	while (receive_msg()){
	    // this prevents the Teensy from being stuck in infinite loop
	    clearing_counter++;
	    if (clearing_counter>10000000){
			break;
        }
		
	}
	

}



//===========================================================================
//====== COMMUNICATION ======
//===========================================================================

bool TeensyUnit::receive_msg(){

	noInterrupts();
	uint8_t byteCount = 0;
	byteCount = RawHID.recv(recv_data_buff, 0);
	interrupts();

	if (byteCount > 0) {
		
		
		// extract the front and end signatures
		byte front_signature = recv_data_buff[0];
		byte back_signature = recv_data_buff[num_incoming_byte-1];

		// compose reply message
		this->compose_reply(front_signature, back_signature);
		send_msg();
		return true;
	}
	else{
		return false;
	}
}

void TeensyUnit::send_msg(){

	// Send a message
	noInterrupts();
	RawHID.send(send_data_buff, 10);
	interrupts();
}




