#ifndef _BEHAVIOUR_H
#define _BEHAVIOUR_H

#include "Arduino.h"
#include "teensy_unit.h"



class Behaviours : public TeensyUnit{

	public:
		
		//--- Constructor and destructor ---
		Behaviours();
		~Behaviours();

		//---- indicator LED -----
		void led_blink_behaviour(uint32_t curr_time);
		void led_wave_behaviour(uint32_t curr_time);
		
		//----- Protocell reflex -----
		void protocell_reflex(uint32_t curr_time);
		
		//--- Tentacle reflex ----
		void tentacle_reflex(uint32_t curr_time);
		
		//--- sound module reflex ---
		void sound_module_reflex(uint32_t curr_time);
		
		
		
	private:

		
		

	
};

#endif
