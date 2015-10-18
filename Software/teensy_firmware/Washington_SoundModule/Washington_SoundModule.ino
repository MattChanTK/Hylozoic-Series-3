
#include <Audio.h>
#include <Wire.h>
#include <SPI.h>
#include <SD.h>

#include "sound_module.h"

const uint8_t LED_PIN = 13;

const uint8_t NUM_BUFF = 2;
int recvMsg[NUM_BUFF];

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
	//first buffer is always the message type
	
	if (recvMsg[0] > 0){
		
		Serial.print("Received Message -- ");
		Serial.print(recvMsg[0]);
		Serial.print(": ");
		Serial.println(recvMsg[1]);
		
		clearRecvMsg();
	}


		// sound_module.setVolume(volume);
		// //sound_module.playWav("test.wav", 1, 1);
		// sound_module.playWav("1.wav", 2, 1);

		// volume += 0.2;
		
		// if (volume > 1.2){
			// volume = 0.1;
		// }
		// delay(1000);
		//recvMsg = 0;

	

}

