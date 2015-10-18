#include "sound_port.h"

//===========================================================================
//====== Sound Port ======
//===========================================================================
//~~constructor and destructor~~
TeensyUnit::SoundPort::SoundPort(TeensyUnit& teensy_parent, const uint8_t Port_Id):
			teensy_unit(teensy_parent),
			port_id(Port_Id),
			is_all_slow(Port_Id==2 || Port_Id==5)
			
{
	
	//----- Pin assignment -----
	if (is_all_slow){
		trigger_pins[0] = teensy_unit.SPWM_pin[port_id][0];
		trigger_pins[1] = teensy_unit.SPWM_pin[port_id][1];
	}
	else{
		trigger_pins[0] = teensy_unit.FPWM_pin[port_id][0];
		trigger_pins[1] = teensy_unit.FPWM_pin[port_id][1];
	}
	
	i2c_pin = teensy_unit.I2C_MUL_ADR[port_id];
	
}

TeensyUnit::SoundPort::~SoundPort(){
	
}

void TeensyUnit::SoundPort::init(){

	delay(5);

}
//~~outputs~~

void TeensyUnit::SoundPort::set_output_level(const uint8_t id, const uint8_t level){
	
	
}
void TeensyUnit::SoundPort::set_digital_trigger(const uint8_t id, const bool on){

	if (id >= 0 && id < 2){
		if (is_all_slow){
			noInterrupts();
			teensy_unit.spwm.setPWMFast(trigger_pins[id], 16*255*on);
			interrupts();
		}
		else{
			digitalWrite(trigger_pins[id], on);
		}
	}
}

//~~inputs~~
bool TeensyUnit::SoundPort::read_analog_state(uint16_t &analog_1, uint16_t &analog_2, uint16_t &analog_3){
	noInterrupts();
	switchToThis();

	teensy_unit.Wire.beginTransmission(SOUND_I2C_ADDR);
	// teensy_unit.Wire.write(1);
	// teensy_unit.Wire.write(1);
	// teensy_unit.Wire.write(3);
	// teensy_unit.Wire.write(0);
	// teensy_unit.Wire.write(0);
	teensy_unit.Wire.write(SOUND_I2C_ANALOG_READ);
	teensy_unit.Wire.endTransmission(I2C_STOP, I2C_TIMEOUT);
	teensy_unit.Wire.requestFrom(SOUND_I2C_ADDR, (size_t) 6, I2C_STOP, I2C_TIMEOUT); // Read 6 bytes      
	
	uint8_t i = 0;
	byte buffer[6] = {0};
	
	delay(50);

	while(teensy_unit.Wire.available() && i<6)
	{
		buffer[i] = teensy_unit.Wire.read();
		i++;
	}
			
	interrupts();

	analog_1 = buffer[1] << 8 | buffer[0];
	analog_2 = buffer[3] << 8 | buffer[2];
	analog_3 = buffer[5] << 8 | buffer[4];
	
	Serial.println(analog_1);
	
	if (i >= 5)
		return true;
	else
		return false;
}

// switching to the this sound module
void TeensyUnit::SoundPort::switchToThis() {

	digitalWrite (teensy_unit.I2C_MUL_ADR_pin[0], (i2c_pin & 1) > 0);
	digitalWrite (teensy_unit.I2C_MUL_ADR_pin[1], (i2c_pin & 2) > 0);
	digitalWrite (teensy_unit.I2C_MUL_ADR_pin[2], (i2c_pin & 4) > 0);
  
}

// Write a value to address register on device
void TeensyUnit::SoundPort::writeToDevice(const byte address, const byte val) {

	switchToThis();
	noInterrupts();
	teensy_unit.Wire.beginTransmission(SOUND_I2C_ADDR); // start transmission to device 
	teensy_unit.Wire.write(address);            // send register address
	teensy_unit.Wire.write(val);                // send value to write
	teensy_unit.Wire.endTransmission(I2C_NOSTOP, I2C_TIMEOUT);         // end transmission
	interrupts();
}

