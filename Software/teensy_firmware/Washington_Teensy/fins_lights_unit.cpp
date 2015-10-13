#include "fins_lights_unit.h"

//===========================================================================
//===== CONSTRUCTOR and DECONSTRUCTOR =====
//===========================================================================

FinsLightsUnit::FinsLightsUnit(uint8_t fin0_port_id=0, 
							   uint8_t fin1_port_id=1, 
							   uint8_t fin2_port_id=2,
							   uint8_t light0_port_id=3, 
							   uint8_t light1_port_id=4, 
							   uint8_t light2_port_id=5
							   ):
	fin0(*this, fin0_port_id), 
	fin1(*this, fin1_port_id), 
	fin2(*this, fin1_port_id), 
	fin{fin0, fin1, fin2},
	light0(*this, light0_port_id),
	light1(*this, light1_port_id),
	light2(*this, light2_port_id),
	light{light0, light1, light2}
{
	
}

FinsLightsUnit::~FinsLightsUnit()
{
	
}

//===========================================================================
//===== INITIALIZATION =====
//===========================================================================
void FinsLightsUnit::init(){

	//--- initialization in the base class
	TeensyUnit::init();
	
	//---- initialize I2C accelerometer on Fin module ---
	fin0.init();
	fin1.init();
	fin2.init();
}