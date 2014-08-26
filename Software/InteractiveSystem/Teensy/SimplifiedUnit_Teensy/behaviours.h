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
		
		//----- Protocell reflex -----
		void protocell_reflex(uint32_t curr_time);
		
		//--- Tentacle reflex ----
		void tentacle_reflex(uint32_t curr_time);
		
		//--- sound module reflex ---
		void sound_module_reflex(uint32_t curr_time);
		
		
		
	private:

		//----- Protocell reflex -----
		bool high_power_led_cycling = false;
		uint32_t protocell_reflex_phase_time= 0;
		
		//--- Tentacle reflex ----
		bool tentacle_reflex_cycling = false;
		uint32_t tentacle_reflex_phase_time = 0;

		//--- sound module reflex ---
		bool sound_module_cycling = false;
		uint32_t sound_module_reflex_phase_time = 0;

};

#endif
