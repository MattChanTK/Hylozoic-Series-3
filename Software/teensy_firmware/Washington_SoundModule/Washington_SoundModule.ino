
#include <Audio.h>
#include <Wire.h>
#include <SPI.h>
#include <SD.h>


#include "sound_module.h"

void setup(){
	Serial.begin(9600);
	delay(1000);
}

void loop(){
	
	static SoundModule sound_module;

	
	sound_module.playWav("test.wav", 0, 1);
	
	delay(500);
}