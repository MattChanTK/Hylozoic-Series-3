
#include <Audio.h>
#include <Wire.h>
#include <SPI.h>
#include <SD.h>

#include "sound_module.h"

const uint8_t LED_PIN = 13;

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
	//--- Set up the audio board ----
	sound_module.audio_board_setup();
	Wire.begin(i2c_device_addr);
	delay(100);
	Wire.onReceive(receiveEvent);
	Wire.onRequest(requestEvent);

	delay(1000);
	
	// sound_module.setVolume(10, 0, 0);
	
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

void requestEvent() {
	
	if (sound_module.requested_data_type == SoundModule::CMD_READ_ANALOG){
		for (uint8_t i=0; i<3; i++){
			Wire.write(lowByte(sound_module.analog_data[i]));
			Wire.write(highByte(sound_module.analog_data[i]));
		}
	}
	// else if (sound_module.requested_data_type == SoundModule::CMD_IS_PLAYING){
		// for (uint8_t i=0; i<4; i++){
			// Wire.write(sound_module.is_playing_L[i]);
		// }
		// for (uint8_t i=0; i<4; i++){
			// Wire.write(sound_module.is_playing_R[i]);
		// }
	// }
}

uint32_t last_bg_on = millis();
int sound_id_0 = 0;
int sound_id_1 = 0;

void loop(){

	uint32_t curr_time = millis();
	// If received message
	// first buffer is always the message type
	// // Serial.println(curr_time);
	// if (recvMsg[0] > 0){
		
		// Serial.print("Received Message -- ");
		// Serial.print(recvMsg[0]);
		// Serial.print(": ");
		// Serial.println(recvMsg[1]);
		
		// sound_module.decodeMsg(recvMsg);
		// clearRecvMsg();
	// }
	
	//==== Basic Code ===
	int delay_time = 1000;
	int ir0 = sound_module.read_analog_state(0);
	int ir1 = sound_module.read_analog_state(1);
	
	// Random Mode
	sound_id_0 = random(1, 6);
	sound_id_1 = random(1, 6);
	
	// Playlist Mode
	// sound_id_0 += 1;
	// if (sound_id_0 > 6){
		// sound_id_0 = 1;
	// }
	// sound_id_1 += 1;
	// if (sound_id_1 > 6){
		// sound_id_1 = 1;
	// }
	
	bool bg_on = false; 

	// if (curr_time - last_bg_on > 1000){
		// bg_on = random(1, 10) <= 2;
		
		// last_bg_on = millis();

	// }
	// Serial.println(bg_on);
	if ((ir0 > 1000)){
		//concatenate file id and extension to a string
		String filename_string = String(sound_id_0) + ".wav";
		char filename [filename_string.length()]; // allocate memeory the char_arr
		filename_string.toCharArray(filename, filename_string.length()+1); // convert String to char_arr
	
		sound_module.playWav(filename, 1, 0, 1);
		
	}
	if ((ir1 > 1000)){
		//concatenate file id and extension to a string
		String filename_string = String(sound_id_1) + ".wav";
		char filename [filename_string.length()]; // allocate memeory the char_arr
		filename_string.toCharArray(filename, filename_string.length()+1); // convert String to char_arr
	
		sound_module.playWav(filename, 2, 0, 1);
	}
	
	//>>>> Light <<<<<
	// starting a cycle
	if (( ir0 > 1000 || ir1 > 1000 || bg_on) && !cycling){
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
		if (cycle_time > 3000){
			
			volatile uint32_t ramping_time = curr_time - step_time;
			
			if (ramping_time > next_step_time){
				for (uint8_t output_id=0; output_id<2; output_id++){
					if (led_level[output_id] > 0) 
						led_level[output_id] -= 1;
				}
				next_step_time += 1;
				step_time = millis();  	
			}
			
			bool end_cycling = true;
			for (uint8_t output_id=0; output_id<2; output_id++){
				end_cycling &= led_level[output_id] <= 0 ;
			}
			if (end_cycling){
				cycling = 0;
			}
			
		}
		//hold steady
		else if (cycle_time > 2000){
			
		}
		// ramping up
		else{
			volatile uint32_t ramping_time = curr_time - step_time;
			
			if (ramping_time > next_step_time){
				
				if (led_level[0] < light_max_level) 
					led_level[0] += 1;
				if (cycle_time > 500){
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


