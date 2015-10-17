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
	

	//--- I2C initialization ----
	//Wire.begin(I2C_MASTER,0x00, I2C_PINS_18_19, I2C_PULLUP_EXT, I2C_RATE_400);
	
	
	//--- Set up the audio board ----
	audio_board_setup();
}

SoundModule::~SoundModule(){

}

//===========================================================================
//===== INITIALIZATION =====
//===========================================================================

void SoundModule::audio_board_setup(){
	Serial.println("Audio Board setup started");

	// Audio connections require memory to work.  For more
	// detailed information, see the MemoryAndCpuUsage example

	AudioMemory(20); // Establish Audio Memory

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
	Serial.println("Audio Board setup finished");

}
void SoundModule::init(){
	

}

//==== Play Wav file ===
//channel: 1=left; 2=right; else=both
//port: if not 1 <= port <= 4, port = 1
bool SoundModule::playWav(char* wavfile, uint8_t channel, uint8_t port){
	

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
	while (playWav_L[port-1].isPlaying() || playWav_R[port-1].isPlaying()) {

	}
	return true;
}

//==== Adjust volume ===
//channel: 1=left; 2=right; else=both
//port: if not 1 <= port <= 4, port = all
void SoundModule::changeVolume(float gain, uint8_t channel, uint8_t port){
	
	if (gain < 0){
		gain = 0;
	}
	
	if (port < 1 || port > 4){
		for (uint8_t i = 0; i < 4; i++){
			if (channel != 2){
				mixer_left.gain(i, gain);
			}
			
			if (channel != 1 ){
				mixer_right.gain(i, gain);
			}
		}
	}
	else{
		
		if (channel != 2){
			mixer_left.gain(port, gain);
		}
		
		if (channel != 1 ){
			mixer_right.gain(port, gain);
		}
	}
}