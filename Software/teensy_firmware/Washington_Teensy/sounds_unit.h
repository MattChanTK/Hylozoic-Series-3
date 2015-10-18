#ifndef _SOUND_UNIT_H
#define _SOUND_UNIT_H

#include "Arduino.h"
#include "teensy_unit.h"
#include "sound_port.h"


class SoundsUnit: public TeensyUnit{
	
	public:
		//===============================================
		//==== Constructor and destructor =====
		//===============================================
		SoundsUnit(uint8_t sound0_port_id, 
				   uint8_t sound1_port_id, 
				   uint8_t sound2_port_id,
				   uint8_t sound3_port_id, 
				   uint8_t sound4_port_id, 
				   uint8_t sound5_port_id
				   );
		~SoundsUnit();
		
		//--- Initialization ---
		void init();
		
		
		
		//===============================================
		//==== Ports ====
		//===============================================
		
		static const uint8_t NUM_SOUND = 6;
		
		SoundPort sound0;
		SoundPort sound1;
		SoundPort sound2;
		SoundPort sound3;
		SoundPort sound4;
		SoundPort sound5;
		SoundPort sound[NUM_SOUND];
	
		
	
};

#endif