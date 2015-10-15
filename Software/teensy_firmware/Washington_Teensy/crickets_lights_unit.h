#ifndef _CRICKETS_UNIT_H
#define _CRICKETS_UNIT_H

#include "Arduino.h"
#include "teensy_unit.h"
#include "device_port.h"


class CricketsLightsUnit: public TeensyUnit{
	
	public:
		//===============================================
		//==== Constructor and destructor =====
		//===============================================
		CricketsLightsUnit(uint8_t cricket0_port_id, 
					 uint8_t cricket1_port_id, 
					 uint8_t cricket2_port_id,
					 uint8_t light0_port_id
					 );
		~CricketsLightsUnit();
		
		//--- Initialization ---
		void init();
		
		
		
		//===============================================
		//==== Ports ====
		//===============================================
		
		static const uint8_t NUM_CRICKET = 3;
		static const uint8_t NUM_LIGHT = 1;
		DevicePort cricket0;
		DevicePort cricket1;
		DevicePort cricket2;
		DevicePort cricket[CricketsLightsUnit::NUM_CRICKET];
		DevicePort light0;
		DevicePort light[CricketsLightsUnit::NUM_LIGHT];
		
		
	
};

#endif