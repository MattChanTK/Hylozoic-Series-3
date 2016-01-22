#include "light_port.h"

//===========================================================================
//====== Light Port ======
//===========================================================================
//~~constructor and destructor~~
TeensyUnit::LightPort::LightPort(TeensyUnit& teensy_parent, const uint8_t Port_Id):
			teensy_unit(teensy_parent),
			port_id(Port_Id),
			is_slow(Port_Id==2 || Port_Id==5)
			
{

	//----- Pin assignment -----
	
	if (is_slow){
		led_pin = teensy_unit.SPWM_pin[port_id][0];
	}
	else{
		led_pin = teensy_unit.FPWM_pin[port_id][0];
	}
	
	analog_pin = teensy_unit.Analog_pin[port_id][0];

}

TeensyUnit::LightPort::~LightPort(){
	
}


//~~outputs~~
void TeensyUnit::LightPort::set_led_level(const uint8_t level){

	if (is_slow){
		noInterrupts();
		teensy_unit.spwm.setPWMFast(led_pin, 16*level);
		interrupts();
	}
	else{
		analogWrite(led_pin, level);
	}
}

//~~inputs~~
uint16_t TeensyUnit::LightPort::read_analog_state(){  
	return (uint16_t) analogRead(analog_pin);
}