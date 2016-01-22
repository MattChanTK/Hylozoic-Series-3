#ifndef _SOUND_PORT_H
#define _SOUND_PORT_H
#include "teensy_unit.h"

class TeensyUnit::SoundPort{

	public:
	
		//~~constructor and destructor~~
		SoundPort(TeensyUnit& teensy_parent, const uint8_t Port_Id);
		~SoundPort();
		void init();

		//~~outputs~~
    bool check_alive();
		
		//--- PWM output ----
		void set_output_level(const uint8_t id, const uint8_t level);
		
		//--- Digital Trigger Input ----
		void set_digital_trigger(const uint8_t id, const bool on);
		
		//--- Play Sound ---
		void play_sound(const uint8_t file_id, const uint8_t volume, const uint8_t channel, const uint8_t port, const bool block);
		
		//~~inputs~~
	
		//--- Analogue Input ----
		bool read_analog_state(uint16_t &analog_1, uint16_t &analog_2, uint16_t &analog_3);
			

		
		//~~configurations~~
		const uint8_t port_id;
		const bool is_all_slow;
		uint8_t trigger_pins[2];
		uint8_t i2c_pin;
		
	private:
	
		TeensyUnit& teensy_unit;
		
		
		//~~Sound Module I2C constants~~
			
		const uint8_t  SOUND_I2C_ADDR = 13; //I2C Address    

    //TODO: THIS SHOULD NOT BE DEFINED IN TWO PLACES
    // Ping to see if it's alive
    static const uint8_t CMD_CHECK_ALIVE = 0; // Commands should be 0-indexed anyways
    
		//--- Read Analog ---
		const uint8_t CMD_READ_ANALOG = 1;
		
		//--- PWM Output ---
		const uint8_t CMD_PWM_OUTPUT = 2;
		
		//byte 1 - PWM ID
		//byte 2 - PWM Level (0...255)
		
		//--- WAV Player ----
		const uint8_t CMD_PLAY_WAV = 3;
		
		// byte 1 - File ID 
		// byte 2 - Volume
		// byte 3 - Channel
		// byte 4 - Port

					
		
		void switchToThis(); // switching to the correct device on the multiplexer
		void writeToDevice(const byte address, const byte val);
		
			
};

#endif
	
