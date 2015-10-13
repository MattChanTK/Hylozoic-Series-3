#ifndef _FINS_LIGHTS_UNIT_H
#define _FINS_LIGHTS_UNIT_H

#include "Arduino.h"
#include "teensy_unit.h"
#include "fin_port.h"
#include "light_port.h"

#define NUM_FIN 3
#define NUM_LIGHT 3

class FinsLightsUnit: public TeensyUnit{
	
	public:
		//===============================================
		//==== Constructor and destructor =====
		//===============================================
		FinsLightsUnit();
		~FinsLightsUnit();
		
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