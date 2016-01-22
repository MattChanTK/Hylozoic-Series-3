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
	
	switchToThis();
	noInterrupts();
	teensy_unit.Wire.beginTransmission(SOUND_I2C_ADDR);
	teensy_unit.Wire.write(CMD_PWM_OUTPUT);
	teensy_unit.Wire.write(id);
	teensy_unit.Wire.write(level);
	teensy_unit.Wire.endTransmission(I2C_STOP, I2C_TIMEOUT);
	interrupts();
	delay(5);

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

void TeensyUnit::SoundPort::play_sound(const uint8_t file_id, const uint8_t volume, const uint8_t channel, const uint8_t port, const bool block){
	switchToThis();
	noInterrupts();
	teensy_unit.Wire.beginTransmission(SOUND_I2C_ADDR);
	teensy_unit.Wire.write(CMD_PLAY_WAV);
	teensy_unit.Wire.write(file_id);
	teensy_unit.Wire.write(volume);
	teensy_unit.Wire.write(channel);
	teensy_unit.Wire.write(port);
	teensy_unit.Wire.write(block);
	teensy_unit.Wire.endTransmission(I2C_STOP, I2C_TIMEOUT);
	interrupts();
	delay(5);

}

//~~inputs~~
bool TeensyUnit::SoundPort::read_analog_state(uint16_t &analog_1, uint16_t &analog_2, uint16_t &analog_3){
	
	switchToThis();
	noInterrupts();
	teensy_unit.Wire.beginTransmission(SOUND_I2C_ADDR);
	teensy_unit.Wire.write(CMD_READ_ANALOG);
	teensy_unit.Wire.endTransmission(I2C_STOP, I2C_TIMEOUT);
	teensy_unit.Wire.requestFrom(SOUND_I2C_ADDR, (size_t) 6, I2C_STOP, I2C_TIMEOUT); // Read 6 bytes      
	interrupts();
	delay(5);

	uint8_t i = 0;
	byte buffer[6] = {0};
	noInterrupts();
	while(teensy_unit.Wire.available() && i<6)
	{
		buffer[i] = teensy_unit.Wire.read();
		i++;
	}
	interrupts();

	analog_1 = buffer[1] << 8 | buffer[0];
	analog_2 = buffer[3] << 8 | buffer[2];
	analog_3 = buffer[5] << 8 | buffer[4];
	
	// Serial.println(analog_1);
	// Serial.println(analog_2);
	// Serial.println(analog_3);
	
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

