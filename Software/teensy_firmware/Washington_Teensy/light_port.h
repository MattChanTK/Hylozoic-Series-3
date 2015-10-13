#include "teensy_unit.h"

class TeensyUnit::LightPort{
	public:
	
		//~~constructor and destructor~~
		LightPort(TeensyUnit& teensy_parent, const uint8_t Port_Id);
		~LightPort();

		//~~outputs~~
		void set_led_level(const uint8_t level);
		
		//~~inputs~~
		uint16_t read_analog_state(); 
		
		
		//~~configurations~~
		const uint8_t port_id;
		const bool is_slow;
		uint8_t led_pin;
		uint8_t analog_pin;
		
	private:
		TeensyUnit& teensy_unit;
	
	
};