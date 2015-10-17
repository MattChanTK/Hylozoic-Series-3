#ifndef _SOUND_MODULE_H
#define _SOUND_MODULE_H



#include "Arduino.h"
#include <Audio.h>
#include <Wire.h>
#include <SPI.h>
#include <SD.h>

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
		//void receiveEvent(int bytes);
		
		//--- Play WAV file ----
		bool playWav(char* wavfile, uint8_t channel=0, uint8_t port=0);
		
		//--- Adjust Volume ----
		void changeVolume(float gain, uint8_t channel=0, uint8_t port=0);
			
		
		
	protected:
		
		//==== I2C object ====
		//i2c_t3 Wire;
		
		//==== constants ====
		
		// Signal processing
		static const int bins = 512; // Number of bins in FFT
		const float fs = 44117.647; //Sampling rate
		const float dF = fs/bins/2.0; // width of FFT bin in Hz
		const float sf = 3.0; // Scaling Factor of FFT values in DB calculation
		const float lowF = 200; // Low frequency cutoff for stats calculations
		const float highF = 6000; // High Frequency cutoff for FFT

		//==== variables ===
		
		// file management
		uint16_t minFileID = 1;
		uint16_t maxFileID = 100;
		
		//Signal processing
		float SCG; // Spectral Center of Gravity
		float aV;
		int mFdata[2];
		float cf[SoundModule::bins];
		float valFFT[SoundModule::bins];
		float dBvalFFT[SoundModule::bins];
		
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
