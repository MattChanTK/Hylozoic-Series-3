#ifndef _SOUND_MODULE_H
#define _SOUND_MODULE_H

#define __USE_I2C_T3__

#include "Arduino.h"

// Audio System
#include <Audio.h>
#ifdef __USE_I2C_T3__
#include <i2c_t3.h> // Had to edit control_wm8731.cpp and control_sgtl5000.cpp to use i2c_t3.h instead of Wire.h
#else
#include <Wire.h>
#endif
#include <SPI.h>
#include <SD.h>
#include <String.h>

#include "rawhid_communicator.h"

#define I2C_TIMEOUT 1000 //microsecond

#define SDCARD_CS_PIN    10
#define SDCARD_MOSI_PIN  7
#define SDCARD_SCK_PIN   14

/*  Holds state variables and constants for sound module instances
*/
struct SoundModuleState {
	uint16_t freqPlay; // The frequency that is being played
	uint16_t freqDetect; // The frequency that is being detected
};

class SoundModule : public RawHIDCommunicator {

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

	void audio_board_setup();

	//--- I2C Communication ---

	//--- Play WAV file ----
	bool playWav(char* wavfile, uint8_t channel = 0, uint8_t port = 0, bool block = false);

	//--- Adjust Volume ----
	void setVolume(uint16_t gain, uint8_t channel = 0, uint8_t port = 0);

	//--- PWM output ----
	void set_output_level(const uint8_t id, const uint8_t level);

	//--- Analogue Input ----
	uint16_t read_analog_state(const uint8_t id);

	//--- Digital Input ----
	bool read_digital_state(const uint8_t id);

	//--- Input functions----
	void sample_inputs();
	

	//===============================================
	//==== Communication functions =====
	//===============================================
	
	void parse_msg();
	void compose_reply(byte front_signature, byte back_signature, byte msg_setting);

	//===============================================
	//==== I2C Communication Protocol ====
	//===============================================

	void decodeMsg(uint8_t* recvMsg);

	// Ping to see if it's alive
	static const uint8_t CMD_CHECK_ALIVE = 0; // Commands should be 0-indexed anyways

	//--- Read Analog ---
	static const uint8_t CMD_READ_ANALOG = 1;

	//--- PWM Output ---
	static const uint8_t CMD_PWM_OUTPUT = 2;

	//byte 1 - PWM ID
	//byte 2 - PWM Level (0...255)

	//--- WAV Player ----
	static const uint8_t CMD_PLAY_WAV = 3;

	// byte 1 - File ID
	// byte 2 - Volume
	// byte 3 - Channel
	// byte 4 - Port
	// byte 5 - Blocking

	// --- Check is playing or not ---
	//static const uint8_t CMD_IS_PLAYING = 4;
	// byte 1 - Left Channel
	// byte 2 - Right Channel

	//==== variables ======
	uint8_t requested_data_type;

	uint16_t analog_data[3];

	// bool is_playing_L[4] = {false, false, false, false};
	// bool is_playing_R[4] = {false, false, false, false};

	// instantiate the audio controller
	AudioControlSGTL5000     sgtl5000_1;

	//===============================================
	//==== Behaviour Functions ====
	//===============================================
	void cbla_behaviour();
	void cpu_analysis();
	
	//protected:


	//==== constants ====


	//==== variables ===

	SoundModuleState state[2];
	
	elapsedMillis playTimer[2], readTimer[2], cpuAnalyzeTimer;


	// GUItool: begin automatically generated code
	AudioSynthWaveformSine   sine_L;          //xy=153.88888549804688,453.8888854980469
	AudioSynthWaveformSine   sine_R;          //xy=153.88888549804688,501.8888854980469
	AudioInputI2S            lineInput;           //xy=165.88888549804688,644.8889465332031
	AudioPlaySdWav           playWav_R2; //xy=169.88888549804688,260.8888854980469
	AudioPlaySdWav           playWav_R1; //xy=171.88888549804688,211.88888549804688
	AudioPlaySdWav           playWav_L1;     //xy=173.88888549804688,112.88888549804688
	AudioPlaySdWav           playWav_L2; //xy=173.88888549804688,160.88888549804688
	AudioEffectEnvelope      envelope_L;      //xy=332.8888854980469,450.888916015625
	AudioEffectEnvelope      envelope_R; //xy=332.8888854980469,505.8888854980469
	AudioAnalyzeFFT256      frequencies_L;      //xy=340.88888655768505,623.8888854980469
	//AudioAnalyzeFFT256      frequencies_R; //xy=340.8888854980469,665.8889465332031
	
	AudioMixer4              mixer_right; //xy=558.888916015625,370.8888854980469
	AudioMixer4              mixer_left;         //xy=559.888916015625,273.8888854980469
	AudioOutputI2S           audio_output;           //xy=775.8889770507812,351.8888854980469
	AudioConnection          patchCord1;//(sine_L, envelope_L);
	AudioConnection          patchCord2;//(sine_R, envelope_R);
	AudioConnection          patchCord3;//(lineInput, 0, frequencies_L, 0);
	//AudioConnection          patchCord4;//(lineInput, 1, frequencies_R, 0);
	AudioConnection          patchCord5;//(playWav_L1, 0, mixer_left, 1);
	AudioConnection          patchCord6;//(playWav_L2, 0, mixer_left, 0);
	AudioConnection          patchCord7;//(playWav_R1, 0, mixer_right, 0);
	AudioConnection          patchCord8;//(playWav_R2, 0, mixer_right, 1);
	AudioConnection          patchCord9;//(envelope_L, 0, mixer_left, 2);
	AudioConnection          patchCord10;//(envelope_R, 0, mixer_right, 2);
	AudioConnection          patchCord11;//(mixer_left, 0, audio_output, 1);
	AudioConnection          patchCord12;//(mixer_right, 0, audio_output, 0);
	// GUItool: end automatically generated code

	
	
	// Input processing
	AudioAnalyzeFFT256      *frequencies[2] = {&frequencies_L, &frequencies_L};
	
	// Audio output
	AudioSynthWaveformSine   *sineWave[2] = {&sine_L, &sine_R};
	AudioEffectEnvelope      *envelope[2] = {&envelope_L, &envelope_R};

	// 4 waves max per mixer
	AudioPlaySdWav			 *playWav_L[2] = {&playWav_L1, &playWav_L2};
	AudioPlaySdWav			 *playWav_R[2] = {&playWav_R1, &playWav_R2};

	int getAudioState(int i);
};
#endif
