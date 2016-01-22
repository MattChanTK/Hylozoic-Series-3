#ifndef _FINS_LIGHTS_UNIT_H
#define _FINS_LIGHTS_UNIT_H

#include "Arduino.h"
#include "teensy_unit.h"
#include "fin_port.h"
#include "device_port.h"


class FinsLightsUnit: public TeensyUnit{
	
	public:
		//===============================================
		//==== Constructor and destructor =====
		//===============================================
		FinsLightsUnit(uint8_t fin0_port_id=0, 
					   uint8_t fin1_port_id=1, 
					   uint8_t fin2_port_id=2,
					   uint8_t light0_port_id=3, 
					   uint8_t light1_port_id=4, 
					   uint8_t light2_port_id=5
					   );
		~FinsLightsUnit();
		
		//--- Initialization ---
		void init();
		
		
		
		//===============================================
		//==== Ports ====
		//===============================================
		static const uint8_t NUM_FIN = 3;
		static const uint8_t NUM_LIGHT = 3;
		FinPort fin0;
		FinPort fin1;
		FinPort fin2;
		FinPort fin[NUM_FIN];
		DevicePort light0;
		DevicePort light1;
		DevicePort light2;
		DevicePort light[NUM_LIGHT];
	
};

#endif