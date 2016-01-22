#ifndef _FINS_SINGLELIGHTS_UNIT_H
#define _FINS_SINGLELIGHTS_UNIT_H

#include "Arduino.h"
#include "teensy_unit.h"
#include "fin_port.h"
#include "light_port.h"

#define NUM_FIN 3
#define NUM_LIGHT 3

class FinsSingleLightsUnit: public TeensyUnit{
	
	public:
		//===============================================
		//==== Constructor and destructor =====
		//===============================================
		FinsSingleLightsUnit(uint8_t fin0_port_id=0, 
					   uint8_t fin1_port_id=1, 
					   uint8_t fin2_port_id=2,
					   uint8_t light0_port_id=3, 
					   uint8_t light1_port_id=4, 
					   uint8_t light2_port_id=5
					   );
		~FinsSingleLightsUnit();
		
		//--- Initialization ---
		void init();
		
		
		
		//===============================================
		//==== Ports ====
		//===============================================
		FinPort fin0;
		FinPort fin1;
		FinPort fin2;
		FinPort fin[NUM_FIN];
		LightPort light0;
		LightPort light1;
		LightPort light2;
		LightPort light[NUM_LIGHT];
	
};

#endif
