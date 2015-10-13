#include "fin_port.h"

//===========================================================================
//====== Fin Port ======
//===========================================================================
//~~constructor and destructor~~
TeensyUnit::FinPort::FinPort(TeensyUnit& teensy_parent, const uint8_t Port_Id):
			teensy_unit(teensy_parent),
			port_id(Port_Id),
			is_all_slow(Port_Id==2 || Port_Id==5)
			
{
	
	//----- Pin assignment -----

	
	if (is_all_slow){
		led_pins[0] = teensy_unit.SPWM_pin[port_id][0];
		led_pins[1] = teensy_unit.SPWM_pin[port_id][1];
		sma_pins[0] = teensy_unit.SPWM_pin[port_id][2];
		sma_pins[1] = teensy_unit.SPWM_pin[port_id][3];
	}
	else{
		led_pins[0] = teensy_unit.FPWM_pin[port_id][0];
		led_pins[1] = teensy_unit.FPWM_pin[port_id][1];
		sma_pins[0] = teensy_unit.SPWM_pin[port_id][0];
		sma_pins[1] = teensy_unit.SPWM_pin[port_id][1];
	}
	

	analog_pins[0] = teensy_unit.Analog_pin[port_id][0];
	analog_pins[1] = teensy_unit.Analog_pin[port_id][1];
	
	acc_pin = teensy_unit.I2C_MUL_ADR[port_id];
	
}

TeensyUnit::FinPort::~FinPort(){
	
}

void TeensyUnit::FinPort::init(){

	//---- initialize acceleromter ---
	writeToAccel(ACC_ACT_ADDR, ACC_ACT_VAL);  
	writeToAccel(ACC_BW_ADDR, ACC_BW_VAL);
	writeToAccel(ACC_BW_ADDR, ACC_BW_VAL);
	writeToAccel(ACC_PWRCTRL_ADDR, ACC_PWRCTRL_SLEEP | ACC_PWRCTRL_MEASURE);
	writeToAccel(ACC_INRPPT_ADDR, ACC_INRPPT_DISABLE);
	writeToAccel(ACC_DATAFORMAT_ADDR, ACC_DATAFORMAT_VALUE);
	writeToAccel(ACC_FIFO_ADDR, ACC_FIFO_VALUE);

	delay(5);

}
//~~outputs~~
void TeensyUnit::FinPort::set_sma_level(const uint8_t id, const uint8_t level){
	
	noInterrupts();
	teensy_unit.spwm.setPWMFast(sma_pins[id], 16*level);
	interrupts();
	
}
void TeensyUnit::FinPort::set_led_level(const uint8_t id, const uint8_t level){

	if (is_all_slow){
		noInterrupts();
		teensy_unit.spwm.setPWMFast(led_pins[id], 16*level);
		interrupts();
	}
	else{
		analogWrite(led_pins[id], level);
	}
}

//~~inputs~~
uint16_t TeensyUnit::FinPort::read_analog_state(const uint8_t id){  //{IR 0, IR 1}
	return (uint16_t) analogRead(analog_pins[id]);
}

bool TeensyUnit::FinPort::read_acc_state(int16_t &accel_x, int16_t &accel_y, int16_t &accel_z){ // return array:{x, y, z}
	
	noInterrupts();
	switchToAccel();

	teensy_unit.Wire.beginTransmission(ACCEL);
	teensy_unit.Wire.write(ACC_X_LSB_ADDR);
	teensy_unit.Wire.endTransmission(I2C_STOP, I2C_TIMEOUT);
	
	teensy_unit.Wire.requestFrom(ACCEL, (size_t) 6, I2C_STOP, I2C_TIMEOUT); // Read 6 bytes      
	
	uint8_t i = 0;
	byte buffer[6] = {0};
	
	//delay(5);

	while(teensy_unit.Wire.available() && i<6)
	{
		buffer[i] = teensy_unit.Wire.read();
		i++;
	}
			
	interrupts();

	accel_x = buffer[1] << 8 | buffer[0];
	accel_y = buffer[3] << 8 | buffer[2];
	accel_z = buffer[5] << 8 | buffer[4];
	
	if (i >=5)
		return true;
	else
		return false;
}

//~~accelerometer~~
// switching to the proper accel
void TeensyUnit::FinPort::switchToAccel() {

	digitalWrite (teensy_unit.I2C_MUL_ADR_pin[0], (acc_pin & 1) > 0);
	digitalWrite (teensy_unit.I2C_MUL_ADR_pin[1], (acc_pin & 2) > 0);
	digitalWrite (teensy_unit.I2C_MUL_ADR_pin[2], (acc_pin & 4) > 0);
  
}

// Write a value to address register on device
void TeensyUnit::FinPort::writeToAccel(const byte address, const byte val) {

	switchToAccel();
	noInterrupts();
	teensy_unit.Wire.beginTransmission(ACCEL); // start transmission to device 
	teensy_unit.Wire.write(address);            // send register address
	teensy_unit.Wire.write(val);                // send value to write
	teensy_unit.Wire.endTransmission(I2C_NOSTOP, I2C_TIMEOUT);         // end transmission
	interrupts();
}

