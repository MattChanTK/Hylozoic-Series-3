#ifndef _LIGHT_H
#define _LIGHT_H

class LightUnitVar{

	private:
	
		friend class WashingtonCricketNode;
		friend class WashingtonFinNode;
	
		//----INPUT----
		uint16_t ir_state[2] = {0, 0};
		
		//----OUTPUT (internal variables)----
		uint32_t phase_time = 0;
		uint32_t step_time = 0;
		bool cycling = false;
		uint32_t next_step_time = 0;
		
		//----OUTPUT (actuators)----
		
		//~~individual PWM level~~~		
		// 4 LED Chains per Light Unit
		uint8_t led_level[4] = {0, 0, 0, 0};
		

};

#endif
