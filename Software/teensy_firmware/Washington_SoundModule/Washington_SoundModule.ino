#define __USE_I2C_T3__
#define __USE_SERIALCOMMAND__
//#define __DEBUG__
#define DEBUG_FREQUENCY 500

#include <Audio.h>
#ifdef __USE_I2C_T3__
#include <i2c_t3.h> // Had to edit control_wm8731.cpp and control_sgtl5000.cpp to use i2c_t3.h instead of Wire.h
#else
#include <Wire.h>
#endif
#include <SPI.h>
#include <SD.h>

#include "T3Mac.h"

#include "sound_module.h"
#include "proximity.h"

#define N_SOUNDS 170

#ifdef __USE_SERIALCOMMAND__
#include <SerialCommand.h>
SerialCommand sCmd (&Serial);     // The demo SerialCommand object
#endif

// IR Sensor defines and variables
#define N_IR 2
#define IR_DECAY 0.001
#define PROXIMITY_THRESHOLD 0.9
Proximity ir[N_IR];
const uint8_t ir_pins[] = {A6, A14};

#ifdef __DEBUG__
// Debug messages
elapsedMillis sensorMessageDelay[2], sensorTrigMessageDelay[2];
#endif

const uint8_t NUM_BUFF = 6;

const uint8_t i2c_device_addr = 13;

uint8_t recvMsg[NUM_BUFF]; // first BUFF is always the message type


SoundModule sound_module;
bool cycling = false;
uint32_t phase_time = millis();
uint32_t step_time = millis();
uint32_t next_step_time = 1;
uint8_t led_level[2] = {0, 0};
const uint8_t light_max_level = 255;

bool audio_cycling = false;
uint32_t audio_phase_time = millis();
uint32_t audio_step_time = millis();
uint32_t audio_next_step_time = 1;

void clearRecvMsg() {
	for (uint8_t i = 0; i < NUM_BUFF; i++) {
		recvMsg[i] = 0;
	}
}

enum OperationMode{
	SelfRunning,
	Manual,
	CBLA,
	Inactive = 255
};
//TODO: Watchdog Timer

// Heartbeat Timer
elapsedMillis heartbeatTimer;
bool heartbeatToggle;

void setup() {

	Serial.begin(9600);

	// set up the indicator LED
	pinMode(LED_BUILTIN, OUTPUT);

	// clear buffer
	clearRecvMsg();

	// initialize the I2C
	//--- Set up the audio board ----
	sound_module.audio_board_setup();
	delay(100);

	Wire.begin(i2c_device_addr);
	delay(100);
	Wire.onReceive(receiveEvent);
	Wire.onRequest(requestEvent);

	delay(100);

	// sound_module.setVolume(10, 0, 0);

	for (int i = 0; i < N_IR; i++) {
		ir[i].init(ir_pins[i], IR_DECAY);
	}

	// Reads in the MAC address from T3Mac.h. Stored as uint8_t mac[6]
	read_mac();



#ifdef __USE_SERIALCOMMAND__
	sCmd.addCommand("VER", cmdVersion);          // Prints version
	sCmd.addCommand("BLINK", cmdBlink);          // Blinks lights
	sCmd.addCommand("VOL", cmdVolume);          // Changes volume
	sCmd.addCommand("MAC", cmdMAC);          // Prints MAC Address
	sCmd.addCommand("I2CSTAT", cmdI2CStatus);          // Prints I2C Status
	sCmd.addCommand("CONF", cmdConfigPrint);          // Prints Configuration
#endif
	
	
	enableWatchdog();
}

void receiveEvent(unsigned int bytes) {
	//Serial.print("Got a message from the Control Node: ");
	for (uint8_t i = 0; i < bytes; i++) {
		if (i >= NUM_BUFF) {
			//BUFFER Full
			break;
		}
		recvMsg[i] = Wire.read();
	}
	Serial.print("Received a message from the Control Node: ");
	for( int i=NUM_BUFF; i >= 0; i-- ){
		Serial.print(recvMsg[i]);
		Serial.print(" ");
	}
	switch (recvMsg[0]) {
	case SoundModule::CMD_CHECK_ALIVE:{
			Serial.print("| Check Alive");
			break;
		}
		// Analog read
	case SoundModule::CMD_READ_ANALOG:{ //TODO This should not need a message? DK
			Serial.print("| Read Analog Values");
			break;
		}
		// PWM Output
	case SoundModule::CMD_PWM_OUTPUT:{
			Serial.print("| PWM Output");
			break;
		}
		// Play Wav File
	case SoundModule::CMD_PLAY_WAV:{
			Serial.print("| Play Sound");
			break;
		}
	default:{
			break;
		}
	}
	Serial.println();
}

void requestEvent() {

	Serial.print("Got a request for data from the Control Node: ");
	Serial.println(sound_module.requested_data_type);

	switch(sound_module.requested_data_type){
	case SoundModule::CMD_CHECK_ALIVE: {
			Wire.write(lowByte(mac[0]));
			break;
		}
	case SoundModule::CMD_READ_ANALOG:
		for (uint8_t i = 0; i < 3; i++) {
			Wire.write(lowByte(sound_module.analog_data[i]));
			Wire.write(highByte(sound_module.analog_data[i]));
		}
		break;
		// else if (sound_module.requested_data_type == SoundModule::CMD_IS_PLAYING){
		// for (uint8_t i=0; i<4; i++){
		// Wire.write(sound_module.is_playing_L[i]);
		// }
		// for (uint8_t i=0; i<4; i++){
		// Wire.write(sound_module.is_playing_R[i]);
		// }
		// }
	}
}

uint32_t last_bg_on = millis();

// From other code in Washinton_Teensy
uint16_t loop_since_last_msg = 0;
const uint16_t keep_alive_thres = 2000;
volatile uint16_t prev_operation_mode = 0;

uint16_t LOOP_PERIOD = 200;
elapsedMillis loop_time;

void loop() {
	
	kickWatchdog(); // Make sure the Watchdog Timer doesn't expire

	uint32_t curr_time = millis();

	if (sound_module.receive_msg()){

		// parse the message and save to parameters
		sound_module.parse_msg();

		loop_since_last_msg = 0;

	}


	// Change what you're doing based on the current operation mode
	if (sound_module.operation_mode != prev_operation_mode){
		Serial.print("Operation Mode: ");
		Serial.println(sound_module.operation_mode);
		prev_operation_mode = sound_module.operation_mode;
	}
	switch (sound_module.operation_mode){
	case SelfRunning: 
		//cbla_mode();
		self_running_test();
		break;
	case Manual:
		if (loop_since_last_msg > keep_alive_thres){
			inactive_mode();
		}
		else{
			manual_mode();
		}
		break;
	case CBLA:
		if (loop_since_last_msg > keep_alive_thres){
			inactive_mode();
		}
		else{
			cbla_mode();
		}
		break;
	default:
		inactive_mode();
		break;
	}

	heartbeat();
	sound_module.cpu_analysis();


	#ifdef __USE_SERIALCOMMAND__
	sCmd.readSerial();     // We don't do much, just process serial commands
	#endif
	
	//wait if not enough time has passed
	int16_t remain_time = LOOP_PERIOD - loop_time;
	if (remain_time > 0){
		Serial.print("Remaining Time: ");
		Serial.println(remain_time);
		delay(remain_time);
	}
	loop_time = 0;
}

// Blink the indicator LED to know it's alive
void heartbeat() {
	if ( heartbeatTimer > 500 ) {
		heartbeatTimer = 0;
		heartbeatToggle = !heartbeatToggle;
		digitalWrite(LED_BUILTIN, heartbeatToggle);
	}
}

void self_running_test(){
	uint32_t curr_time = millis();
	//==== Basic Code ===

	//Update IR readings
	for (int i = 0; i < N_IR; i++) {
		ir[i].read();
	}

	bool bg_on = false;

	if (curr_time - last_bg_on > 1000){
		bg_on = random(1, 10) <= 2;

		last_bg_on = millis();

	}

	// Test proximity sensors and play sound if seen
	for( int i=0; i < N_IR; i++){
		if ((ir[i].value() > PROXIMITY_THRESHOLD)) {
			#ifdef __DEBUG__
			if( sensorTrigMessageDelay[i] > DEBUG_FREQUENCY ){
				Serial.print("Proximity Sensor ");
				Serial.print(i);
				Serial.print(" Found: reading ");
				Serial.print(ir[i].reading);
				Serial.print(" | normal ");
				Serial.print(ir[i].value());
				Serial.print(" | ");
				Serial.print(ir[i].limits.decay_minimum());
				Serial.print(" | ");
				Serial.print(ir[i].limits.average());
				Serial.print(" | ");
				Serial.println(ir[i].limits.decay_maximum());
				sensorTrigMessageDelay[i] = 0;
			}
			#endif
			
			int sound_id = random(1, N_SOUNDS);
			//concatenate file id and extension to a string
			String filename_string = String(sound_id) + ".wav";
			char filename [filename_string.length()]; // allocate memeory the char_arr
			filename_string.toCharArray(filename, filename_string.length() + 1); // convert String to char_arr

			sound_module.playWav(filename, i+1, 0, 1);

		}
		#ifdef __DEBUG__
		if( sensorMessageDelay[i] > DEBUG_FREQUENCY ){
			Serial.print("Proximity Sensor ");
			Serial.print(i);
			Serial.print(": reading ");
			Serial.print(ir[i].reading);
			Serial.print(" | normal ");
			Serial.print(ir[i].value());
			Serial.print(" | ");
			Serial.print(ir[i].limits.decay_minimum());
			Serial.print(" | ");
			Serial.print(ir[i].limits.average());
			Serial.print(" | ");
			Serial.println(ir[i].limits.decay_maximum());
			sensorMessageDelay[i] = 0;
		}
		#endif
	}

	//>>>> Light <<<<<
	//starting a cycle
	if (( ir[0].value() > PROXIMITY_THRESHOLD || ir[1].value() > PROXIMITY_THRESHOLD || bg_on) && !cycling) {
		Serial.println("starting cycle");
		cycling = true;
		phase_time = millis();
		step_time = millis();
		next_step_time = 2;
	}
	else if (cycling) {

		volatile uint32_t cycle_time = curr_time - phase_time;

		//ramping down
		// if reaches the full period, restart cycle
		if (cycle_time > 3000) {

			volatile uint32_t ramping_time = curr_time - step_time;

			if (ramping_time > next_step_time) {
				for (uint8_t output_id = 0; output_id < 2; output_id++) {
					if (led_level[output_id] > 0)
					led_level[output_id] -= 1;
				}
				next_step_time += 1;
				step_time = millis();
			}

			bool end_cycling = true;
			for (uint8_t output_id = 0; output_id < 2; output_id++) {
				end_cycling &= led_level[output_id] <= 0 ;
			}
			if (end_cycling) {
				cycling = 0;
			}

		}
		//hold steady
		else if (cycle_time > 2000) {

		}
		// ramping up
		else {
			volatile uint32_t ramping_time = curr_time - step_time;

			if (ramping_time > next_step_time) {

				if (led_level[0] < light_max_level)
				led_level[0] += 1;
				if (cycle_time > 500) {
					if (led_level[1] < light_max_level)
					led_level[1] += 2;
				}
				next_step_time += 1;
				step_time = millis();
			}

		}
	}

	sound_module.set_output_level(0, led_level[0]);
	sound_module.set_output_level(1, led_level[1]);
}

void manual_mode(){}
void inactive_mode(){}
void cbla_mode(){
	
	sound_module.cbla_behaviour();
	
}

#ifdef __USE_SERIALCOMMAND__
void cmdVersion() {
	Serial.println("TEENSY SOFTWARE COMPILED: " __DATE__ " " __TIME__);
}

void cmdBlink() {
	Serial.println("Blinking...");
	for ( int i = 0; i < 10; i++ ) {
		sound_module.set_output_level(0, 255);
		sound_module.set_output_level(1, 0);
		delay(10);
		sound_module.set_output_level(0, 0);
		sound_module.set_output_level(1, 255);
		delay(10);
	}
	sound_module.set_output_level(0, 0);
	sound_module.set_output_level(1, 0);
	Serial.println("Done Blinking...");
}

// Changes volume to x in "VOL x" where x=0-9
void cmdVolume(){
	int vol = 0;
	char *arg;

	arg = sCmd.next();
	if( arg != NULL ){    
		vol = atoi(arg);
		sound_module.sgtl5000_1.dacVolume(((float)vol)/9.0); // Digitally adjusts volume from 0.0-1.0
		
		Serial.print("Set volume to ");
		Serial.println(((float)vol)/9.0);
	} else {
		Serial.println("Volume could not be set. Argument was NULL. [" __FILE__ ": " "__LINE__" "]");
	}

}

// Prints the Teensy's MAC address
void cmdMAC(){
	print_mac();
	Serial.println();
}

// Print the Code's Configuration Flags
void cmdConfigPrint(){
	Serial.print("Config: ");
	Serial.print("Debug[");
#ifdef __DEBUG__
	Serial.print("y");
#else
	Serial.print("n");
#endif
	Serial.print("] i2c_t3[");
#ifdef __USE_I2C_T3__
	Serial.print("y");
#else
	Serial.print("n");
#endif
	Serial.print("] SerialCommand[");
#ifdef __USE_SERIALCOMMAND__
	Serial.print("y");
#else
	Serial.print("n");
#endif
	Serial.println("]");

}

// Print the I2C Status
void cmdI2CStatus(){
	print_i2c_status();
}

//
// print I2C status
//
void print_i2c_status(void)
{
	switch(Wire.status())
	{
	case I2C_WAITING:  Serial.print("I2C waiting, no errors\n"); break;
	case I2C_ADDR_NAK: Serial.print("Slave addr not acknowledged\n"); break;
	case I2C_DATA_NAK: Serial.print("Slave data not acknowledged\n"); break;
	case I2C_ARB_LOST: Serial.print("Bus Error: Arbitration Lost\n"); break;
	case I2C_TIMEOUT:  Serial.print("I2C timeout\n"); break;
	case I2C_BUF_OVF:  Serial.print("I2C buffer overflow\n"); break;
	case I2C_SENDING:  Serial.print("I2C sending\n"); break;
	case I2C_SEND_ADDR: Serial.print("I2C send addr\n"); break;
	case I2C_RECEIVING: Serial.print("I2C receiving\n"); break;
	case I2C_SLAVE_TX: Serial.print("I2C slave TX\n"); break;
	case I2C_SLAVE_RX: Serial.print("I2C slave RX\n"); break;
	default:           Serial.print("I2C busy\n"); break;
	}
}
#endif

void enableWatchdog(){
	WDOG_UNLOCK = WDOG_UNLOCK_SEQ1;
	WDOG_UNLOCK = WDOG_UNLOCK_SEQ2;
	delayMicroseconds(1); // Need to wait a bit..
	WDOG_STCTRLH = 0x0001; // Enable WDG
	WDOG_TOVALL = 2000; // The next 2 lines sets the time-out value. This is the value that the watchdog timer compare itself to in milliseconds
	WDOG_TOVALH = 0;
	WDOG_PRESC = 0; // This sets prescale clock so that the watchdog timer ticks at 1kHZ instead of the default 1kHZ/4 = 200 HZ
}

void kickWatchdog(){
	noInterrupts();
	WDOG_REFRESH = 0xA602;
	WDOG_REFRESH = 0xB480;
	interrupts();
}

