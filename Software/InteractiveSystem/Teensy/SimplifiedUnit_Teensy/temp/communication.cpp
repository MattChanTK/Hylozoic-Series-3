

//===========================================================================
//===========================================================================

//====== COMMUNICATION CODES ======

boolean receive_msg(byte recv_data_buff[], byte send_data_buff[]){

	noInterrupts();
	unsigned short byteCount = RawHID.recv(recv_data_buff, 0);
	interrupts();

	if (byteCount > 0) {
		
		// sample the sensors
		sample_inputs();
		
		// extract the front and end signatures
		byte front_signature = recv_data_buff[0];
		byte back_signature = recv_data_buff[numIncomingByte-1];

		// compose reply message
		compose_reply(send_data_buff, front_signature, back_signature);
		send_msg(send_data_buff);
		return true;
	}
	else{
		return false;
	}
}

void send_msg(byte data_buff[]){

	// Send a message
	noInterrupts();
	RawHID.send(data_buff, 10);
	interrupts();
}

void parse_msg(byte data_buff[]){
	int val = 0;
        
	// byte 2 --- indicator led on or off
	indicator_led_on = data_buff[2];

	// byte 3 and 4 --- indicator led blinking frequency
	val = 0;
	for (int i = 0; i < 2 ; i++)
	  val += data_buff[i+3] << (8*i);
	indicator_led_blinkPeriod = val*1000;

	// byte 5 --- high power LED level
	high_power_led_level = data_buff[5];
        
	// byte 6 and byte 7 --- high power LED reflex threshold
	val = 0;
	for (int i = 0; i < 2 ; i++)
	  val += data_buff[i+6] << (8*i);
	high_power_led_reflex_threshold = val;
	
	// byte 8 --- SMA 0 level
	sma_0_level = data_buff[8];
	
	// byte 9 --- SMA 1 level
	sma_1_level = data_buff[9];
	
	// byte 10 --- Reflex 0 level
	reflex_0_level = data_buff[10];
	
	// byte 11 --- Reflex 1 level
	reflex_1_level = data_buff[11];

}

void compose_reply(byte data_buff[], byte front_signature, byte back_signature){

	// add the signatures to first and last byte
	data_buff[0] = front_signature;
	data_buff[numOutgoingByte-1] = back_signature;

	// byte 1 and 2 --- analog 0
	for (int i = 0; i < 2 ; i++)
		data_buff[i+1] = analog_0_state >> (8*i);

	// byte 3 and 4 --- ambient light sensor
	for (int i = 0; i < 2 ; i++)
		data_buff[i+3] = ambient_light_sensor_state >> (8*i);
	
	// byte 5 and 6 --- IR 0 state
	for (int i = 0; i < 2 ; i++)
		data_buff[i+5] = ir_0_state >> (8*i);
		
	// byte 7 and 8 --- IR 1 state
	for (int i = 0; i < 2 ; i++)
		data_buff[i+7] = ir_1_state >> (8*i);

}

