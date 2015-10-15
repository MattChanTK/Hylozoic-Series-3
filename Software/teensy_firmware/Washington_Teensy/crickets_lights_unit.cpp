#include "crickets_lights_unit.h"

//===========================================================================
//===== CONSTRUCTOR and DECONSTRUCTOR =====
//===========================================================================

CricketsLightsUnit::CricketsLightsUnit(uint8_t cricket0_port_id, 
									   uint8_t cricket1_port_id, 
									   uint8_t cricket2_port_id,
									   uint8_t light0_port_id
									   ):
							cricket0(*this, cricket0_port_id),
							cricket1(*this, cricket1_port_id),
							cricket2(*this, cricket2_port_id),
							cricket({cricket0, cricket1, cricket2}),
							light0(*this, light0_port_id),
							light({light0})
{
	
}

CricketsLightsUnit::~CricketsLightsUnit()
{
	
}

//===========================================================================
//===== INITIALIZATION =====
//===========================================================================
void CricketsLightsUnit::init(){

	//--- initialization in the base class
	TeensyUnit::init();
	
	//---- initialize I2C accelerometer on cricket module ---
	for (uint8_t i=0; i<CricketsLightsUnit::NUM_CRICKET; i++){
		cricket[i].init();
	}
	
	//---- initialize I2C accelerometer on light module ---
	for (uint8_t i=0; i<CricketsLightsUnit::NUM_LIGHT; i++){
		cricket[i].init();
	}
}