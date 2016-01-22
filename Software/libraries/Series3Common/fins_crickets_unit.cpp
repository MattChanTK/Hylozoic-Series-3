#include "fins_crickets_unit.h"

//===========================================================================
//===== CONSTRUCTOR and DECONSTRUCTOR =====
//===========================================================================

FinsCricketsUnit::FinsCricketsUnit(uint8_t fin0_port_id, 
								   uint8_t fin1_port_id, 
								   uint8_t fin2_port_id,
								   uint8_t cricket0_port_id, 
								   uint8_t cricket1_port_id, 
								   uint8_t cricket2_port_id
								   ):
							fin0(*this, fin0_port_id),
							fin1(*this, fin1_port_id),
							fin2(*this, fin2_port_id),
							fin{fin0, fin1, fin2},
							cricket0(*this, cricket0_port_id),
							cricket1(*this, cricket1_port_id),
							cricket2(*this, cricket2_port_id),
							cricket{cricket0, cricket1, cricket2}
	
{
	
}

FinsCricketsUnit::~FinsCricketsUnit()
{
	
}

//===========================================================================
//===== INITIALIZATION =====
//===========================================================================
void FinsCricketsUnit::init(){

	//--- initialization in the base class
	TeensyUnit::init();
	
	//---- initialize I2C accelerometer on cricket module ---
	for (uint8_t i=0; i<NUM_CRICKET; i++){
		cricket[i].init();
	}
	
	//---- initialize I2C accelerometer on fin module ---
	for (uint8_t i=0; i<NUM_FIN; i++){
		fin[i].init();
	}
}