
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
	
	static float volume = 0.1;
	static SoundModule sound_module;

	sound_module.changeVolume(volume);

	sound_module.playWav("test.wav", 1, 1);
	sound_module.playWav("B.wav", 2, 1);
	
	volume += 0.3;
	
	if (volume > 1.2){
		volume = 0.1;
	}
	
	
	delay(50);
}