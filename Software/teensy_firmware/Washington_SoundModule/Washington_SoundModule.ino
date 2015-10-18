
#include <Audio.h>
#include <Wire.h>
#include <SPI.h>
#include <SD.h>

#include "sound_module.h"

const uint8_t LED_PIN = 13;

const uint8_t NUM_BUFF = 6;

const uint8_t i2c_device_addr = 13;

uint8_t recvMsg[NUM_BUFF]; // first BUFF is always the message type


SoundModule sound_module;


void clearRecvMsg(){
	for (uint8_t i = 0; i < NUM_BUFF; i++){
		recvMsg[i] = 0;
	}
}

void setup(){
	
	Serial.begin(9600);
	
	// set up the indicator LED
    pinMode (LED_PIN, OUTPUT);
	
	// clear buffer
	clearRecvMsg();
	
	// initialize the I2C
	//--- Set up the audio board ----
	sound_module.audio_board_setup();
	Wire.begin(i2c_device_addr);
	delay(100);
	Wire.onReceive(receiveEvent);
	Wire.onRequest(requestEvent);

	delay(1000);
	
}

void receiveEvent(int bytes) {
	for (uint8_t i = 0; i < bytes; i++){
		if (i >= NUM_BUFF){
			//BUFFER Full
			break;
		}
		recvMsg[i] = Wire.read();
	}
}

void requestEvent() {
	
	if (sound_module.requested_data_type == SoundModule::CMD_READ_ANALOG){
		for (uint8_t i=0; i<3; i++){
			Wire.write(lowByte(sound_module.analog_data[i]));
			Wire.write(highByte(sound_module.analog_data[i]));
		}
	}
	// else if (sound_module.requested_data_type == SoundModule::CMD_IS_PLAYING){
		// for (uint8_t i=0; i<4; i++){
			// Wire.write(sound_module.is_playing_L[i]);
		// }
		// for (uint8_t i=0; i<4; i++){
			// Wire.write(sound_module.is_playing_R[i]);
		// }
	// }
}

void loop(){

	
	// If received message
	// first buffer is always the message type
	if (recvMsg[0] > 0){
		
		Serial.print("Received Message -- ");
		Serial.print(recvMsg[0]);
		Serial.print(": ");
		Serial.println(recvMsg[1]);
		
		sound_module.decodeMsg(recvMsg);
		clearRecvMsg();
	}
	
	//sound_module.playWav("1.wav", 0, 0, 1);


}


