#include "sounds_unit.h"

//===========================================================================
//===== CONSTRUCTOR and DECONSTRUCTOR =====
//===========================================================================

SoundsUnit::SoundsUnit(uint8_t sound0_port_id, 
					   uint8_t sound1_port_id, 
					   uint8_t sound2_port_id,
					   uint8_t sound3_port_id, 
					   uint8_t sound4_port_id, 
					   uint8_t sound5_port_id
					   ):
							sound0(*this, sound0_port_id),
							sound1(*this, sound1_port_id),
							sound2(*this, sound2_port_id),
							sound3(*this, sound3_port_id),
							sound4(*this, sound4_port_id),
							sound5(*this, sound5_port_id),
							sound{sound0, sound1, sound2, sound3, sound4, sound5}
{
	
}

SoundsUnit::~SoundsUnit()
{
	
}

//===========================================================================
//===== INITIALIZATION =====
//===========================================================================
void SoundsUnit::init(){
	
	//--- I2C initialization ----
	// running at 100kHz
	Wire.begin(I2C_MASTER,0x00, I2C_PINS_18_19, I2C_PULLUP_EXT, I2C_RATE_100);
	
	//--- initialization in the base class
	TeensyUnit::init();
	
	
	//---- initialize I2C accelerometer on Sound module ---
	for (uint8_t i=0; i<NUM_SOUND; i++){
		sound[i].init();
	}

}