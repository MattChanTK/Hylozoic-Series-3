#include "sound_module.h"

//===========================================================================
//===== CONSTRUCTOR and DECONSTRUCTOR =====
//===========================================================================
SoundModule::SoundModule():
		wav_mixer_L1(playWav_L[0], 0, mixer_left, 0),
		wav_mixer_L2(playWav_L[1], 0, mixer_left, 1),
		wav_mixer_L3(playWav_L[2], 0, mixer_left, 2),
		wav_mixer_L4(playWav_L[3], 0, mixer_left, 3),
		wav_mixer_R1(playWav_R[0], 0, mixer_right, 0),
		wav_mixer_R2(playWav_R[1], 0, mixer_right, 1),
		wav_mixer_R3(playWav_R[2], 0, mixer_right, 2),
		wav_mixer_R4(playWav_R[3], 0, mixer_right, 3),
		mixer_output_L(mixer_left, 0, audio_output, 0),
		mixer_output_R(mixer_right, 0, audio_output, 1)
		
{

	
	//===============================================
	//==== pin initialization ====
	//===============================================
	uint8_t num_pins = 0;
	
	//--- PWM pins ---

	num_pins = sizeof(PWM_pin)/sizeof(PWM_pin[0]);
	for (uint8_t i = 0; i<num_pins; i++){
		pinMode(PWM_pin[i], OUTPUT);
	}
	
	//--- Analogue pins ---
	num_pins = sizeof(Analog_pin)/sizeof(Analog_pin[0]);
	for (uint8_t i = 0; i<num_pins; i++){
		pinMode(Analog_pin[i], INPUT);
	}
	
	//--- Digital pins ---
	num_pins = sizeof(Digital_pin)/sizeof(Digital_pin[0]);
	for (uint8_t i = 0; i<num_pins; i++){
		pinMode(Digital_pin[i], INPUT);
	}
	
	//--- Analogue settings ---
	analogReadResolution(12);
	analogReadAveraging(32);
	analogWriteResolution(8);
	
	

}

SoundModule::~SoundModule(){

}

//===========================================================================
//===== INITIALIZATION =====
//===========================================================================

void SoundModule::audio_board_setup(){

	// Audio connections require memory to work.  For more
	// detailed information, see the MemoryAndCpuUsage example

	AudioMemory(30); // Establish Audio Memory

	// configuration
	sgtl5000_1.enable(); // Enable LINE-OUT
	sgtl5000_1.volume(0.8); //Set Iniitial LINE-OUT Gain
	sgtl5000_1.dacVolume(1.0);
	sgtl5000_1.adcHighPassFilterEnable();
	// sgtl5000_1.audioPreProcessorEnable();
	// sgtl5000_1.enhanceBassEnable();
	sgtl5000_1.lineOutLevel(29);
	mixer_left.gain(1, 0.8);
	mixer_right.gain(1, 0.8);

	SPI.setMOSI(SDCARD_MOSI_PIN);
	SPI.setSCK(SDCARD_SCK_PIN);
	
	 // Check SD card is present and readable
	if (!(SD.begin(SDCARD_CS_PIN))){
		// stop here, but print a message repetitively
		while (1) {
			Serial.println("Unable to access the SD card");
			delay(500);
		}
	}

}
void SoundModule::init(){
	

}

//==== Play Wav file ===
//channel: 1=left; 2=right; else=both
//port: if not 1 <= port <= 4, port = 1
bool SoundModule::playWav(char* wavfile, uint8_t channel, uint8_t port, bool block){
	

	Serial.print("Playing file: ");
	Serial.println(wavfile);
	
	if (port < 1 || port > 4){
		port = 1;
	}
	
	bool fileFound = true;


	// Start playing the file.  This sketch continues to
	// run while the file plays.
	if (channel != 2){
		fileFound &= playWav_L[port-1].play(wavfile);
	}
	
	if (channel != 1 ){
		fileFound &= playWav_R[port-1].play(wavfile);
	}
	
	if (!fileFound)
		return false;

	// A brief delay for the library read WAV info
	delay(5);
	
	// Simply wait for the file to finish playing.
	while (block && (playWav_L[port-1].isPlaying() || playWav_R[port-1].isPlaying())) {

	}
	return true;
}

//==== Adjust volume ===
//channel: 1=left; 2=right; else=both
//port: if not 1 <= port <= 4, port = all
//Volume: 0 = min (silent), 25 = 0.5x, 50 = 1x, 100 = 2x
void SoundModule::setVolume(uint16_t gain, uint8_t channel, uint8_t port){
	
	if (gain < 0){
		gain = 0;
	}
	else if (gain > 100){
		gain = 100;
	}
	float gain_f = 0.02*gain;
	
	if (port < 1 || port > 4){
		for (uint8_t i = 0; i < 4; i++){
			if (channel != 2){
				mixer_left.gain(i, gain_f);
			}
			
			if (channel != 1 ){
				mixer_right.gain(i, gain_f);
			}
		}
	}
	else{
		
		if (channel != 2){
			mixer_left.gain(port, gain_f);
		}
		
		if (channel != 1 ){
			mixer_right.gain(port, gain_f);
		}
	}
}

//==== Set Output Level ===
void SoundModule::set_output_level(const uint8_t id, const uint8_t level){
	if (id >= 0 && id < 2){
		analogWrite(PWM_pin[id], level);
	}
}

//==== Analogue Input ====
uint16_t SoundModule::read_analog_state(const uint8_t id){
	if (id >= 0 && id < 3){
		return analogRead(Analog_pin[id]);
	}
	return 0;
}

//==== Digital Input ====
bool SoundModule::read_digital_state(const uint8_t id){
	if (id >= 0 && id < 2){
		return digitalRead(Digital_pin[id]);
	}
	return 0;
}

//===============================================
//==== I2C Communication Protocol ====
//===============================================
		
void SoundModule::decodeMsg(uint8_t* recvMsg){
	
	uint8_t cmd_type = recvMsg[0];
	
	switch(cmd_type){
		
		// Analog read
		case SoundModule::CMD_READ_ANALOG:{
			
			requested_data_type = CMD_READ_ANALOG;
			// sample data from analog ports
			for (uint8_t i=0; i<3; i++){
				analog_data[i] = read_analog_state(i);
			}
			break;
		}
		
		// PWM Output
		case SoundModule::CMD_PWM_OUTPUT:{
			
			// byte 1 - PWM ID
			uint8_t pwm_id = recvMsg[1];
			// byte 2 - PWM Level (0...255)
			uint8_t pwm_level = recvMsg[2];
			
			// output to PWM
			set_output_level(pwm_id, pwm_level);
			
			break;
		}
		
		// Play Wav File
		case SoundModule::CMD_PLAY_WAV:{
			
			// byte 1 - File ID 
			uint8_t file_id = recvMsg[1];
			
			//concatenate file id and extension to a string
			String filename_string = String(file_id) + ".wav";
			char filename [filename_string.length()]; // allocate memeory the char_arr
			filename_string.toCharArray(filename, filename_string.length()+1); // convert String to char_arr
			
			// byte 2 - Volume
			uint8_t volume = (uint8_t) recvMsg[2];
			
			// byte 3 - Channel
			uint8_t channel = (uint8_t) recvMsg[3];
			
			// byte 4 - Port
			uint8_t port = (uint8_t) recvMsg[4];
			
			// byte 5 - Blocking
			bool blocking = recvMsg[5] > 0;
			
			// set volume
			setVolume(volume, channel, port);
			
			// play sound
			playWav(filename, channel, port, blocking);
	
			break;
		}
		// Is Playing or Not
		// case SoundModule::CMD_IS_PLAYING:{
			
			// requested_data_type = CMD_IS_PLAYING;
			// for (uint8_t i =0; i < 4; i++){
				// is_playing_L[i] = playWav_L[i].isPlaying();
				// is_playing_R[i] = playWav_L[i].isPlaying();
			// }
			// break;
		// 
		default:{
			break;
		}
	}

			
}
