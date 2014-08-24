#ifndef _BEHAVIOUR_H
#define _BEHAVIOUR_H

#include "Arduino.h"
#include "system_config.h"

//--- Input Sampling ----
//~~Teensy on-board~~
extern volatile unsigned int analog_0_state;
//~~IR sensors state~~
extern volatile unsigned int ir_0_state;
extern volatile unsigned int ir_1_state;
//~~Ambient light sensor state~~
extern volatile unsigned int ambient_light_sensor_state;
//~~Sound_moudle states~~
extern volatile boolean sound_detect_state;
extern volatile unsigned int sound_module_ir_state;
//~~Sampling function~~
void sample_inputs();


//---- indicator LED blinking -----
//~~indicator LED on~~
extern volatile boolean indicator_led_on; //exposed
extern volatile boolean indicator_led_on_0;
//~~indicator LED blink~~
extern IntervalTimer indicator_led_blinkTimer;
extern volatile int indicator_led_blinkPeriod_0;
extern volatile int indicator_led_blinkPeriod; //exposed
void blinkLED(void);
void led_blink_behaviour();


//----- Protocell reflex -----
//~~output~~
extern volatile unsigned short high_power_led_level;  //exposed
extern volatile int high_power_led_reflex_enabled;
extern volatile boolean high_power_led_cycling;
extern const unsigned short high_power_led_level_max;
extern volatile unsigned int high_power_led_reflex_threshold;
//~~timing~~
extern volatile unsigned long protocell_reflex_phase_time;
void protocell_reflex(unsigned long curr_time);


//--- Tentacle reflex ----
//~~output~~
extern volatile boolean tentacle_reflex_enabled;
extern volatile boolean tentacle_reflex_cycling;
extern volatile unsigned short sma_0_level; //exposed
extern volatile unsigned short sma_1_level; //exposed
extern volatile unsigned short reflex_0_level; //exposed
extern volatile unsigned short reflex_1_level; //exposed
extern volatile unsigned int ir_0_threshold;
extern volatile unsigned int ir_1_threshold;
//~~timing~~
extern volatile unsigned long tentacle_reflex_phase_time;
void tentacle_reflex(unsigned long curr_time);


//--- sound module reflex ---
//~~output~~
extern volatile boolean sound_module_reflex_enabled;
extern volatile boolean sound_module_cycling;
//~~timing~~
extern volatile unsigned long sound_module_reflex_phase_time;
void sound_module_reflex(unsigned long curr_time);

#endif
