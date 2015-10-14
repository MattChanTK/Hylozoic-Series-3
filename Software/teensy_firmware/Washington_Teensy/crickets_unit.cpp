#include "crickets_unit.h"

//===========================================================================
//===== CONSTRUCTOR and DECONSTRUCTOR =====
//===========================================================================

CricketsUnit::CricketsUnit(uint8_t cricket0_port_id, 
						   uint8_t cricket1_port_id, 
						   uint8_t cricket2_port_id,
						   uint8_t cricket3_port_id, 
						   uint8_t cricket4_port_id, 
						   uint8_t cricket5_port_id
						   ):
	cricket0(*this, cricket0_port_id), 
	cricket1(*this, cricket1_port_id), 
	cricket2(*this, cricket2_port_id), 
	cricket3(*this, cricket3_port_id), 
	cricket4(*this, cricket4_port_id), 
	cricket5(*this, cricket5_port_id), 
	cricket{cricket0, cricket1, cricket2, cricket3, cricket4, cricket5}
{
	
}

CricketsUnit::~CricketsUnit()
{
	
}

//===========================================================================
//===== INITIALIZATION =====
//===========================================================================
void CricketsUnit::init(){

	//--- initialization in the base class
	TeensyUnit::init();
	
	//---- initialize I2C accelerometer on cricket module ---
	for (uint8_t i=0; i<NUM_CRICKET; i++){
		cricket[i].init();
	}
}