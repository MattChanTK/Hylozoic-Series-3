#ifndef _CRICKETS_UNIT_H
#define _CRICKETS_UNIT_H

#include "Arduino.h"
#include "teensy_unit.h"
#include "device_port.h"

#define NUM_CRICKET 6

class CricketsUnit: public TeensyUnit{
	
	public:
		//===============================================
		//==== Constructor and destructor =====
		//===============================================
		CricketsUnit(uint8_t cricket0_port_id, 
					 uint8_t cricket1_port_id, 
					 uint8_t cricket2_port_id,
					 uint8_t cricket3_port_id, 
					 uint8_t cricket4_port_id, 
					 uint8_t cricket5_port_id
					 );
		~CricketsUnit();
		
		//--- Initialization ---
		void init();
		
		
		
		//===============================================
		//==== Ports ====
		//===============================================
		DevicePort cricket0;
		DevicePort cricket1;
		DevicePort cricket2;
		DevicePort cricket3;
		DevicePort cricket4;
		DevicePort cricket5;
		DevicePort cricket[NUM_CRICKET];
	
};

#endif