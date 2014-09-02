#include "teensy_unit.h"

//===========================================================================
//===== CONSTRUCTOR and DECONSTRUCTOR =====
//===========================================================================

TeensyUnit::TeensyUnit()
	:sma_0_wave(sma_0_pin) {
	

	//==== Teensy On-Board=====
	//---- indicator led ----
	pinMode(indicator_led_pin, OUTPUT);
	

	//---- analog read -----
	pinMode(analog_0_pin, INPUT);

	//===== Protocell board =====
	//---- high power led ---
	pinMode(high_power_led_pin, OUTPUT);

	//---- ambient light sensor ----
	pinMode(ambient_light_sensor_pin, INPUT);

	//===== Tentacle board ====
	pinMode(sma_0_pin, OUTPUT);
	pinMode(sma_1_pin, OUTPUT);
	pinMode(reflex_0_pin, OUTPUT);
	pinMode(reflex_1_pin, OUTPUT);
	pinMode(ir_0_pin, INPUT);
	pinMode(ir_1_pin, INPUT);
	
	//==== Sound module ====
	pinMode(sound_detect_pin, INPUT);
	pinMode(sound_trigger_pin, OUTPUT);
	pinMode(sound_module_led_0_pin, OUTPUT);
	pinMode(sound_module_led_1_pin, OUTPUT);
	pinMode(sound_module_ir_pin, INPUT);
	pinMode(vbatt_pin, INPUT);
	
	
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
	    if (clearing_counter>10000){
			break;
        }
	}

}



//===========================================================================
//====== COMMUNICATION ======
//===========================================================================

bool TeensyUnit::receive_msg(){

	noInterrupts();
	uint8_t byteCount = RawHID.recv(recv_data_buff, 0);
	interrupts();

	if (byteCount > 0) {
		
		// sample the sensors
		sample_inputs();
		
		// extract the front and end signatures
		byte front_signature = recv_data_buff[0];
		byte back_signature = recv_data_buff[num_incoming_byte-1];

		// compose reply message
		compose_reply(front_signature, back_signature);
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

void TeensyUnit::parse_msg(){

	uint16_t val = 0;
	
	// byte 1 --- type of request
	request_type = recv_data_buff[1];
        
	switch (request_type){
		case 1: {
			// byte 2 to 33 --- indicator LED wave 
			for (short i = 0; i < wave_size; i++)
				sma_0_wave.waveform[i] = recv_data_buff[i+2];
			break;
		}
		default:{
			// byte 2 --- indicator led on or off
			indicator_led_on = recv_data_buff[2];

			// byte 3 and 4 --- indicator led blinking frequency
			val = 0;
			for (short i = 0; i < 2 ; i++)
			  val += recv_data_buff[i+3] << (8*i);
			indicator_led_blink_period = val;

			// byte 5 --- high power LED level
			high_power_led_level = recv_data_buff[5];
				
			// byte 6 and byte 7 --- high power LED reflex threshold
			val = 0;
			for (short i = 0; i < 2 ; i++)
			  val += recv_data_buff[i+6] << (8*i);
			high_power_led_reflex_threshold = val;
			
			// byte 8 --- SMA 0 level
			sma_0_level = recv_data_buff[8];
			
			// byte 9 --- SMA 1 level
			sma_1_level = recv_data_buff[9];
			
			// byte 10 --- Reflex 0 level
			reflex_0_level = recv_data_buff[10];
			
			// byte 11 --- Reflex 1 level
			reflex_1_level = recv_data_buff[11];
			break;
		}
	}

}

void TeensyUnit::compose_reply(byte front_signature, byte back_signature){

	// add the signatures to first and last byte
	send_data_buff[0] = front_signature;
	send_data_buff[num_outgoing_byte-1] = back_signature;

	switch (request_type){
	
		default:
			// byte 1 and 2 --- analog 0
			for (int i = 0; i < 2 ; i++)
				send_data_buff[i+1] = analog_0_state >> (8*i);

			// byte 3 and 4 --- ambient light sensor
			for (int i = 0; i < 2 ; i++)
				send_data_buff[i+3] = ambient_light_sensor_state >> (8*i);
			
			// byte 5 and 6 --- IR 0 state
			for (int i = 0; i < 2 ; i++)
				send_data_buff[i+5] = ir_0_state >> (8*i);
				
			// byte 7 and 8 --- IR 1 state
			for (int i = 0; i < 2 ; i++)
				send_data_buff[i+7] = ir_1_state >> (8*i);
		break;
	}

}

//===========================================================================
//====== Input functions ======
//===========================================================================

//--- Sampling function ---
void TeensyUnit::sample_inputs(){

	analog_0_state = analogRead(analog_0_pin);
	ambient_light_sensor_state = analogRead(ambient_light_sensor_pin);
	ir_0_state = analogRead(ir_0_pin);
	ir_1_state = analogRead(ir_1_pin);
	
}
//===========================================================================
//====== Output functions ======
//===========================================================================



