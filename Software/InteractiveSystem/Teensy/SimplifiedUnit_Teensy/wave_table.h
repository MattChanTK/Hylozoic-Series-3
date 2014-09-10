#ifndef _WAVE_TABLE_H
#define _WAVE_TABLE_H

#include "Arduino.h"

#define wave_size 32

typedef prog_uchar PROGMEM const_wave_t;
typedef uint8_t wave_t;

class WaveTable{

	public:
	
		//--- Constructor and destructor ---
		WaveTable();
		WaveTable(const uint16_t Duration, const float Amplitude, const wave_t Wave[wave_size]);
		~WaveTable();


		//--- Wave function ----
		uint8_t wave_function(const long curr_time);
		
		//--- Wave tables waveform ----
		wave_t waveform[wave_size];
		
		//--- Getter of pwm output ----
		uint8_t get_pwm_output();
		
		//--- Setter and getter of the Waveform ---
		WaveTable& set_wave(const wave_t Wave[wave_size]);
		wave_t* get_wave();
		
		//--- Setters and getters for the configuration parameters ---
		WaveTable& set_duration(const uint16_t Duration);
		uint16_t get_duration() const;
		
		WaveTable& set_amplitude(const float Amplitude);
		float get_amplitude() const;

	
	private:
	
		//--- Granularity ---
		const uint8_t granularity = 15;
		
		//--- configuration parameters ---
		uint16_t duration;
		float amplitude;
		
		//==== WAVE FUNCTION variables ====
		bool wave_function_cycling;
		int32_t wave_function_phase_time;
		uint16_t step_duration;
		uint16_t step_count;
		int8_t level_change;
		uint8_t gran_count;
		
		uint8_t pwm_output = 0; //assumes 8-bit
	
		
		
		
};

#endif