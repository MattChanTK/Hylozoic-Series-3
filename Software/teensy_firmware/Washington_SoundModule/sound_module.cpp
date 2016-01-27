#include "sound_module.h"

#define N_SPEAKERS 2
#define N_FFT_BINS 512

//===========================================================================
//===== CONSTRUCTOR and DECONSTRUCTOR =====
//===========================================================================
SoundModule::SoundModule():
  /*pc_leftFreq(lineInput, 0, frequencies[0], 0),
  pc_rightFreq(lineInput, 0, frequencies[0], 0),
  //frequencies{leftFreq, rightFreq},
  wav_mixer_L1(playWav_L[0], 0, mixer_left, 0),
  wav_mixer_L2(playWav_L[1], 0, mixer_left, 1),
  wav_mixer_R1(playWav_R[0], 0, mixer_right, 0),
  wav_mixer_R2(playWav_R[1], 0, mixer_right, 1),
  patchCord1(sineWave[0], envelope[0]),
  patchCord2(sineWave[1], envelope[1]),
  patchCord3(envelope[0], 0, mixer_left, 2),
  patchCord4(envelope[1], 0, mixer_right, 2),
  mixer_output_L(mixer_left, 0, audio_output, 0),
  mixer_output_R(mixer_right, 0, audio_output, 1)*/
	patchCord1(sine_L, envelope_L),
	patchCord2(sine_R, envelope_R),
	patchCord3(lineInput, 0, frequencies_L, 0),
	patchCord4(lineInput, 1, frequencies_R, 0),
	patchCord5(playWav_L1, 0, mixer_left, 1),
	patchCord6(playWav_L2, 0, mixer_left, 0),
	patchCord7(playWav_R1, 0, mixer_right, 0),
	patchCord8(playWav_R2, 0, mixer_right, 1),
	patchCord9(envelope_L, 0, mixer_right, 2),
	patchCord10(envelope_R, 0, mixer_left, 2),
	patchCord11(mixer_left, 0, audio_output, 1),
	patchCord12(mixer_right, 0, audio_output, 0)
{


  //===============================================
  //==== pin initialization ====
  //===============================================
  uint8_t num_pins = 0;

  //--- PWM pins ---

  num_pins = sizeof(PWM_pin) / sizeof(PWM_pin[0]);
  for (uint8_t i = 0; i < num_pins; i++) {
    pinMode(PWM_pin[i], OUTPUT);
  }

  //--- Analogue pins ---
  num_pins = sizeof(Analog_pin) / sizeof(Analog_pin[0]);
  for (uint8_t i = 0; i < num_pins; i++) {
    pinMode(Analog_pin[i], INPUT);
  }

  //--- Digital pins ---
  num_pins = sizeof(Digital_pin) / sizeof(Digital_pin[0]);
  for (uint8_t i = 0; i < num_pins; i++) {
    pinMode(Digital_pin[i], INPUT);
  }

  //--- Analogue settings ---
  analogReadResolution(12);
  analogReadAveraging(32);
  analogWriteResolution(8);
}

SoundModule::~SoundModule() {

}

//===========================================================================
//===== INITIALIZATION =====
//===========================================================================

void SoundModule::audio_board_setup() {

  // Audio connections require memory to work.  For more
  // detailed information, see the MemoryAndCpuUsage example

  AudioMemory(50); // Establish Audio Memory

  // configuration
  sgtl5000_1.enable(); // Enable LINE-OUT
  sgtl5000_1.volume(0.8); //Set Iniitial LINE-OUT Gain NOPE. Sets only headphones. See docs.
  sgtl5000_1.dacVolume(1.0); // Changed to set volume lower. This also lowers quality :( DK
  sgtl5000_1.adcHighPassFilterEnable();
  // sgtl5000_1.audioPreProcessorEnable();
  // sgtl5000_1.enhanceBassEnable();
  sgtl5000_1.lineOutLevel(29);
  mixer_left.gain(1, 0.8);
  mixer_right.gain(1, 0.8);
  
  sgtl5000_1.inputSelect(AUDIO_INPUT_LINEIN);

  SPI.setMOSI(SDCARD_MOSI_PIN);
  SPI.setSCK(SDCARD_SCK_PIN);

  // Check SD card is present and readable
  if (!(SD.begin(SDCARD_CS_PIN))) {
    // stop here, but print a message repetitively
    while (1) {
      Serial.println("Unable to access the SD card");
      delay(500);
    }
  }

}
void SoundModule::init() {
}

//==== Play Wav file ===
//channel: 1=left; 2=right; else=both
//port: if not 1 <= port <= 4, port = 1
bool SoundModule::playWav(char* wavfile, uint8_t channel, uint8_t port, bool block) {

  if (port < 1 || port > 2) {
    port = 1;
  }

  bool fileFound = true;
  static uint8_t curr_port_L = 0;
  static uint8_t curr_port_R = 0;


  // Start playing the file.  This sketch continues to
  // run while the file plays.
  if (channel != 2) {
    if (!block && playWav_L[curr_port_L]->isPlaying()) {
      //fileFound &= playWav_L[port].play(wavfile);
      curr_port_L += 1;
      if (curr_port_L >= 1)
        curr_port_L = 0;
    }
    if (!(block && playWav_L[port - 1]->isPlaying() )) {
      Serial.print("Playing file on Left: ");
      Serial.println(wavfile);
      fileFound &= playWav_L[curr_port_L]->play(wavfile);
    }

  }

  if (channel != 1 ) {

    if (!block && playWav_R[curr_port_R]->isPlaying()) {
      // fileFound &= playWav_L[curr_port_R].play(wavfile);
      curr_port_R += 1;
      if (curr_port_R >= 1)
        curr_port_R = 0;
    }
    if (!(block && playWav_R[port - 1]->isPlaying() )) {
      Serial.print("Playing file on Right: ");
      Serial.println(wavfile);
      fileFound &= playWav_R[curr_port_R]->play(wavfile);
    }
  }

  if (!fileFound) {
    Serial.print("404 NOT FOUND: ");
    Serial.println(wavfile);
    return false;
  }

  // A brief delay for the library read WAV info
  delay(5);

  //Simply wait for the file to finish playing.
  // while (block &&((playWav_L[port-1].isPlaying() || playWav_R[port-1].isPlaying()))) {

  // }


  return true;
}

//==== Adjust volume ===
//channel: 1=left; 2=right; else=both
//port: if not 1 <= port <= 4, port = all
//Volume: 0 = min (silent), 25 = 0.5x, 50 = 1x, 100 = 2x
void SoundModule::setVolume(uint16_t gain, uint8_t channel, uint8_t port) {

  if (gain < 0) {
    gain = 0;
  }
  else if (gain > 100) {
    gain = 100;
  }
  float gain_f = 0.02 * gain;

  if (port < 1 || port > 4) {
    for (uint8_t i = 0; i < 4; i++) {
      if (channel != 2) {
        mixer_left.gain(i, gain_f);
      }

      if (channel != 1 ) {
        mixer_right.gain(i, gain_f);
      }
    }
  }
  else {

    if (channel != 2) {
      mixer_left.gain(port, gain_f);
    }

    if (channel != 1 ) {
      mixer_right.gain(port, gain_f);
    }
  }
}

//==== Set Output Level ===
void SoundModule::set_output_level(const uint8_t id, const uint8_t level) {
  if (id >= 0 && id < 2) {
    analogWrite(PWM_pin[id], level);
  }
}

//==== Analogue Input ====
uint16_t SoundModule::read_analog_state(const uint8_t id) {
  if (id >= 0 && id < 3) {
    return analogRead(Analog_pin[id]);
  }
  return 0;
}

//==== Digital Input ====
bool SoundModule::read_digital_state(const uint8_t id) {
  if (id >= 0 && id < 2) {
    return digitalRead(Digital_pin[id]);
  }
  return 0;
}

void SoundModule::parse_msg() {
  // byte 1 --- type of request
  request_type = (RequestType) recv_data_buff[1];


  uint16_t temp_val = 0;

  switch (request_type) {

    // Basic
    case RequestType::Basic: {

        // >>>>>> byte 2 to 9: ON-BOARD <<<<<<<

        // byte 2 --- indicator led on or off
        //indicator_led_on = recv_data_buff[2];

        // byte 3 and 4 --- indicator led blinking frequency
        temp_val = 0;
        for (uint8_t i = 0; i < 2 ; i++){
          temp_val += recv_data_buff[3 + i] << (8 * i);
        }
        indicator_led_blink_period = temp_val;

        // >>>> byte 10: CONFIG VARIABLES <<<<<

        // byte 10 ---- operation mode
        operation_mode = recv_data_buff[10];

        // byte 11 ---- reply message type request
        reply_type = (ResponseType)recv_data_buff[11];

        // >>>>> byte 30 to byte 39:
        neighbour_activation_state = recv_data_buff[30];

        break;
      }
      
    // mid level requests
    case RequestType::MidLevel: {

        // First byte and last byte are special codes
        uint8_t  device_offset = 2;

        // (2 bytes each)
        // >>>>> byte 2 to byte 3: Fin 0

        for( int i=0; i<N_SPEAKERS; i++){
          // byte --- frequency to play on speaker i
			playTimer[i] = 0;
          state[i].freqPlay = getInt16(device_offset+2*i);
        }
    }

    // read-only
    case RequestType::ReadOnly: {
        break;
      }
    default: {
        break;
      }

  }

}

//====== Input functions ======

//--- Sampling function ---
void SoundModule::sample_inputs() {
  //=== Sound FFT ===
  for (int j = 0; j < N_SPEAKERS; j++) {
    state[j].freqDetect = getAudioState(j);
  }
}

int SoundModule::getAudioState(int i){
  int max_window_index = 0;
  float max_window_value = 0.0;
  if (frequencies[i]->available()) {
    for( int j=0; j < N_FFT_BINS; j++ ){
      if( frequencies[i]->read(j) > max_window_value ){
        max_window_value = frequencies[i]->read(j);
        max_window_index = j;
      }
    }
  }
  
	Serial.print("Frequency: ");
	Serial.print(max_window_index);
	Serial.print(" | ");
	Serial.println(max_window_value);

  return max_window_index;
}

//====== COMMUNICATION Protocol ======

void SoundModule::compose_reply(byte front_signature, byte back_signature, byte msg_setting) {

  // add the signatures to first and last byte
  send_data_buff[0] = front_signature;
  send_data_buff[num_outgoing_byte - 1] = back_signature;

  if (msg_setting == 0) {
    // sample the sensors
    this->sample_inputs();
  }

  // byte 1 --- type of reply
  send_data_buff[1] =  reply_type;

  switch (reply_type) {

    case ResponseType::Readings:  {

        uint8_t  device_offset = 2;

        // >>>>> byte 2 to byte 15: FIN 0
        // >>>>> byte 16 to byte 29: FIN 1
        // >>>>> byte 30 to byte 43: FIN 2
        for( int i=0; i<N_SPEAKERS; i++ ){
          send_data_buff[device_offset+2*i] = state[i].freqDetect & 0xFF;
          send_data_buff[device_offset+2*i+1] = state[i].freqDetect >> 8;
        }
        
        break;
      }

    // echo
    case ResponseType::Echo: {
        for (uint8_t i = 2; i < 63; i++) {
          send_data_buff[i] = recv_data_buff[i];
        }
        break;
      }
    default: {
        break;
      }

  }
}

//===============================================
//==== I2C Communication Protocol ====
//===============================================

void SoundModule::decodeMsg(uint8_t* recvMsg) {

  uint8_t cmd_type = recvMsg[0];

  switch (cmd_type) {

    case SoundModule::CMD_CHECK_ALIVE: {
        requested_data_type = CMD_CHECK_ALIVE;
        break;
      }
    // Analog read
    case SoundModule::CMD_READ_ANALOG: { //TODO This should not need a message? DK

        requested_data_type = CMD_READ_ANALOG;
        // sample data from analog ports
        for (uint8_t i = 0; i < 3; i++) {
          analog_data[i] = read_analog_state(i);
        }
        break;
      }
    // PWM Output
    case SoundModule::CMD_PWM_OUTPUT: {

        // byte 1 - PWM ID
        uint8_t pwm_id = recvMsg[1];
        // byte 2 - PWM Level (0...255)
        uint8_t pwm_level = recvMsg[2];

        // output to PWM
        set_output_level(pwm_id, pwm_level);

        break;
      }
    // Play Wav File
    case SoundModule::CMD_PLAY_WAV: {

        // byte 1 - File ID
        uint8_t file_id = recvMsg[1];

        //concatenate file id and extension to a string
        String filename_string = String(file_id) + ".wav";
        char filename [filename_string.length()]; // allocate memeory the char_arr
        filename_string.toCharArray(filename, filename_string.length() + 1); // convert String to char_arr

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
    default: {
        break;
      }
  }
  }
  
  
void  SoundModule::cbla_behaviour(){
	  for(int i=0; i<N_SPEAKERS; i++){
		  if(playTimer[i] < 500){
			  sineWave[i]->frequency(state[i].freqPlay);
			  
			  envelope[i]->noteOn();
		  } else {
			  envelope[i]->noteOff();
		  }
	  }
  }

