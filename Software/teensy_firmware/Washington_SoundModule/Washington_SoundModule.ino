
#include <Audio.h>
#include <Wire.h>
#include <SPI.h>
#include <SD.h>

#include "sound_module.h"

const uint8_t LED_PIN = 13;

const uint8_t NUM_BUFF = 6;

uint8_t recvMsg[NUM_BUFF]; // first BUFF is always the message type

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
	Wire.begin(13);
	Wire.onReceive(receiveEvent);
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

void loop(){

	  
	static SoundModule sound_module;
	
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


}


