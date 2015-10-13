#include "fins_lights_unit.h"

//===========================================================================
//===== CONSTRUCTOR and DECONSTRUCTOR =====
//===========================================================================

FinsLightsUnit::FinsLightsUnit():
	fin0(*this, 0), 
	fin1(*this, 0), 
	fin2(*this, 0), 
	fin{fin0, fin1, fin2},
	light0(*this, 3),
	light1(*this, 4),
	light2(*this, 5),
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