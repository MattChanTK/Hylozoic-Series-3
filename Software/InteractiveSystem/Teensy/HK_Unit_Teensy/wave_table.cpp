#include "wave_table.h"

//--- Constructor and destructor ---

WaveTable::WaveTable():
	waveform{0, 2, 9, 21, 37, 56, 78, 102, 127, 151, 175, 197, 216, 232, 244, 251, 254, 251, 244, 232, 216, 197, 175, 151, 127, 102, 78, 56, 37, 21, 9, 2}
{
	duration = 10000;
}
WaveTable::WaveTable(uint16_t Duration):
	waveform{0, 2, 9, 21, 37, 56, 78, 102, 127, 151, 175, 197, 216, 232, 244, 251, 254, 251, 244, 232, 216, 197, 175, 151, 127, 102, 78, 56, 37, 21, 9, 2}
{
	duration = Duration;
}

WaveTable::WaveTable(const uint16_t Duration, const wave_t Wave[wave_size]){
			 
	//copy the waveform to the object
	for (int i = 0; i < wave_size; i++){
		waveform[i] = Wave[i];
	}
	
	//copy the parameters over
	duration = Duration;
		  
}

WaveTable::~WaveTable(){

}


//--- Wave Table Synthesis ---
uint8_t WaveTable::wave_function(const uint32_t& curr_time) {

	// starting a wave cycle
	if (wave_function_cycling == false){
		wave_function_cycling = true;
		wave_function_phase_time = millis();
		step_duration_100 = duration*100/(wave_size) ;
		step_count = 1;
		level_change_1000 = (waveform[1] - waveform[0])*1000/granularity;
			
		pwm_output = (uint8_t) waveform[0];

	}
	else{	
	
		// if reaches full time duration
		if (step_count >= wave_size  || (curr_time - wave_function_phase_time) >= duration){
			wave_function_cycling = false;
			
		}
		// if reaches one time step
		else if ((curr_time - wave_function_phase_time) > step_count*step_duration_100/100){
			pwm_output = (uint8_t) (waveform[step_count]);
			step_count++;
			if (step_count >= wave_size)
				level_change_1000 = (waveform[0] - waveform[wave_size-1])*1000/granularity;
			else
				level_change_1000 = (waveform[step_count] - waveform[step_count-1])*1000/granularity;
			gran_count = 1;
		}
		// if reaches a interpolated step
		else if ((curr_time - wave_function_phase_time) > ((step_count-1)*step_duration_100/100 + (gran_count*step_duration_100/100)/granularity)){
			pwm_output = (uint8_t) (waveform[step_count-1] + gran_count*level_change_1000/1000);
			
			gran_count++;
		}
		// during the step
		else{		
		
		}
	}
	
	return pwm_output;
}

//--- getter for pwm output ----
uint8_t WaveTable::get_pwm_output(){

	return pwm_output;
}


//--- Setter and getter of the Waveform ---
WaveTable& WaveTable::set_wave(const wave_t Wave[wave_size]){

	//copy the waveform to the object
	for (int i = 0; i < wave_size; i++){
		waveform[i] = Wave[i];
	}
	return *this;
}
wave_t* WaveTable::get_wave(){

	return waveform;
}
		
//--- Setters and getters for the configuration parameters ---
WaveTable& WaveTable::set_duration(const uint16_t Duration){
	
	duration = Duration;
	
	return *this;
}

uint16_t WaveTable::get_duration() const{

	return duration;
}

void WaveTable::restart_wave_function(){
	wave_function_cycling == false;
	step_count = 1;
	pwm_output = 0;
	
}
		