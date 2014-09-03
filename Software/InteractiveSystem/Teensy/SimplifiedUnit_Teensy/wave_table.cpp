#include "wave_table.h"

//--- Constructor and destructor ---
WaveTable::WaveTable(const uint8_t Pin_Num){
	
	duration = 1000;
	amplitude = 1.0;
	pin_num = Pin_Num;
	
	//==== WAVE FUNCTION variables ====
	bool wave_function_cycling = false;
	int32_t wave_function_phase_time = 0;
	uint16_t step_duration = 0;
	uint16_t step_count = 0;
	int8_t level_change = 0;
	uint8_t gran_count = 0;
	
	//=== default sine wave ===
	wave_t sine_wave[wave_size] = {127, 233, 242, 144, 30, 5, 91, 210, 252, 179, 57, 0, 58, 180, 252, 209, 90, 4, 31, 146, 242, 233, 125, 19, 11, 110, 223, 248, 161, 42, 1, 75};
	//copy the waveform to the object
	for (int i = 0; i < wave_size; i++){
		waveform[i] = sine_wave[i];
	}
	
}

WaveTable::WaveTable(const uint8_t Pin_Num, const uint16_t Duration, const float Amplitude, const wave_t Wave[wave_size]){
			 
	//copy the waveform to the object
	for (int i = 0; i < wave_size; i++){
		waveform[i] = Wave[i];
	}
	
	//copy the parameters over
	duration = Duration;
	amplitude = Amplitude;
	pin_num = Pin_Num;
	
	//==== WAVE FUNCTION variables ====
	bool wave_function_cycling = false;
	int32_t wave_function_phase_time = 0;
	uint16_t step_duration = 0;
	uint16_t step_count = 0;
	int8_t level_change = 0;
	uint8_t gran_count = 0;
			  
}

WaveTable::~WaveTable(){

}

//--- Wave Table Synthesis ---
void WaveTable::wave_function(const long curr_time) {

	// starting a wave cycle
	if (wave_function_cycling == false){

		wave_function_cycling = true;
		wave_function_phase_time = millis();
		step_duration = duration/(wave_size-1) ;
		step_count = 1;
		level_change = (waveform[1] - waveform[0])/granularity;
				
		analogWrite(pin_num, (uint8_t) waveform[0]*amplitude);
	}
	else if (wave_function_cycling == true){
		
		// if reaches full time duration
		if (step_count >= wave_size  || (curr_time - wave_function_phase_time) >= duration){
			wave_function_cycling = false;
		}
		// if reaches one time step
		else if ((curr_time - wave_function_phase_time) > step_count*step_duration){
			analogWrite(pin_num, (uint8_t) (waveform[step_count]*amplitude));
			step_count++;
			level_change = (waveform[step_count] - waveform[step_count-1])/granularity;
			gran_count = 1;
			
		}
		// if reaches a interpolated step
		else if ((curr_time - wave_function_phase_time) > ((step_count-1)*step_duration + (gran_count*step_duration)/granularity)){
			analogWrite(pin_num, (uint8_t) (waveform[step_count-1] + gran_count*level_change)*amplitude);
			gran_count++;
			
		}
		// during the step
		else{		
			
		
		}
	}
	
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
		
WaveTable& WaveTable::set_amplitude(const float Amplitude){

	amplitude = Amplitude;
	
	return *this;
}

float WaveTable::get_amplitude() const{
	
	return amplitude;
}