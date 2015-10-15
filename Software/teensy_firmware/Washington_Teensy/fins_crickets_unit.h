#ifndef _FINS_CRICKETS_UNIT_H
#define _FINS_CRICKETS_UNIT_H

#include "Arduino.h"
#include "teensy_unit.h"
#include "device_port.h"
#include "fin_port.h"


class FinsCricketsUnit: public TeensyUnit{
	
	public:
		//===============================================
		//==== Constructor and destructor =====
		//===============================================
		FinsCricketsUnit(uint8_t fin0_port_id, 
						 uint8_t fin1_port_id, 
						 uint8_t fin2_port_id,
						 uint8_t cricket0_port_id, 
						 uint8_t cricket1_port_id, 
						 uint8_t cricket2_port_id
						 );
		~FinsCricketsUnit();
		
		//--- Initialization ---
		void init();
		
		
		
		//===============================================
		//==== Ports ====
		//===============================================
		
		static const uint8_t NUM_CRICKET = 3;
		static const uint8_t NUM_FIN = 3;
		
		FinPort fin0;
		FinPort fin1;
		FinPort fin2;
		FinPort fin[NUM_FIN];
		DevicePort cricket0;
		DevicePort cricket1;
		DevicePort cricket2;
		DevicePort cricket[NUM_CRICKET];
	
		
		
	
};

#endif