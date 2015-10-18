#ifndef _SOUND_MODULE_H
#define _SOUND_MODULE_H



#include "Arduino.h"
#include <Audio.h>
#include <Wire.h>
#include <SPI.h>
#include <SD.h>
#include <String.h>
//#include "i2c_t3"

#define I2C_TIMEOUT 1000 //microsecond

#define SDCARD_CS_PIN    10
#define SDCARD_MOSI_PIN  7
#define SDCARD_SCK_PIN   14	


class SoundModule{
	
	public:
	
		//===============================================
		//==== pin assignments ====
		//===============================================
		
		
		//--- PWM outout pins ---
		const uint8_t PWM_pin[2] = {3, 4};
		
		//--- Analogue input pins ---
		const uint8_t Analog_pin[3] = {A6, A7, A14};
		
		//--- Digital input pins ---
		const uint8_t Digital_pin[2] = {1, 2};
				
		
		//===============================================
		//==== Functions ====
		//===============================================
		
		//--- Constructor and destructor ---
		SoundModule();
		~SoundModule();

		//--- Initialization ---
		void init();
		
		//--- I2C Communication ---
		
		//--- Play WAV file ----
		bool playWav(char* wavfile, uint8_t channel=0, uint8_t port=0, bool block=false);
		
		//--- Adjust Volume ----
		void setVolume(uint16_t gain, uint8_t channel=0, uint8_t port=0);
		
		//--- PWM output ----
		void set_output_level(const uint8_t id, const uint8_t level);
		
		//--- Analogue Input ----
		uint16_t read_analog_state(const uint8_t id);
			
		//--- Digital Input ----
		bool read_digital_state(const uint8_t id);
		
		
		//===============================================
		//==== I2C Communication Protocol ====
		//===============================================
		
		void decodeMsg(uint8_t* recvMsg);
	

		//--- Read Analog ---
		static const uint8_t CMD_READ_ANALOG = 1;

		
		//--- PWM Output ---
		static const uint8_t CMD_PWM_OUTPUT = 2;
		
		//--- WAV Player ----
		static const uint8_t CMD_PLAY_WAV_L = 3;
		
		// byte 1 - File ID 
		// byte 2 - Volume
		// byte 3 - Port
		
		static const uint8_t CMD_PLAY_WAV_R = 4;
		
		// byte 1 - File ID 
		// byte 2 - Volume
		// byte 3 - Channel

		
	protected:
		
		
		//==== constants ====
		
		
		//==== variables ===

		
		//Signal processing
		
		// the left and right mixers
		AudioMixer4              mixer_left;         // mixer1 - Left Channel
		AudioMixer4              mixer_right;        // mixer2 - Right Channel
		
		// 4 waves max per mixer	
		AudioPlaySdWav			 playWav_L[4];
		AudioPlaySdWav			 playWav_R[4];
		
		// audio output
		AudioOutputI2S           audio_output;
		
		// Connections between the wav player and the mizer
		AudioConnection          wav_mixer_L1;
		AudioConnection          wav_mixer_L2;
		AudioConnection          wav_mixer_L3;
		AudioConnection          wav_mixer_L4;
		
		AudioConnection          wav_mixer_R1;
		AudioConnection          wav_mixer_R2;
		AudioConnection          wav_mixer_R3;
		AudioConnection          wav_mixer_R4;
		
		// Connections between the mixer and audio output
		AudioConnection			 mixer_output_L;
		AudioConnection			 mixer_output_R;
		
		// instantiate the audio controller 
		AudioControlSGTL5000     sgtl5000_1;

		
		//==== functions =====
		void audio_board_setup();
};
#endif
