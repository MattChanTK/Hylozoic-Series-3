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
		
		//--- PWM output ----
		void set_output_level(const uint8_t id, const uint8_t level);
		
		//--- Digital Trigger Input ----
		void set_digital_trigger(const uint8_t id, const bool on);
		
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
		const uint8_t  SOUND_I2C_ANALOG_READ = 1; //I2C msg

					
		
		void switchToThis(); // switching to the correct device on the multiplexer
		void writeToDevice(const byte address, const byte val);
		
			
};

#endif
	