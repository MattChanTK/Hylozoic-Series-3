#include "teensy_unit.h"


//===========================================================================
//===== CONSTRUCTOR and DECONSTRUCTOR =====
//===========================================================================

TeensyUnit::TeensyUnit(): Wire(0),
	FPWM_pin {FPWM_1_pin, FPWM_2_pin, FPWM_3_pin, FPWM_4_pin, FPWM_5_pin, FPWM_6_pin},
	SPWM_pin {SPWM_1_pin, SPWM_2_pin, SPWM_3_pin, SPWM_4_pin, SPWM_5_pin, SPWM_6_pin}, 
	Analog_pin {Analog_1_pin, Analog_2_pin, Analog_3_pin, Analog_4_pin, Analog_5_pin, Analog_6_pin}
{

	
	//===============================================
	//==== pin initialization ====
	//===============================================

	uint8_t num_ports = 0;
	uint8_t num_pins = 0;
	
	//--- Teensy On-Board ---
	pinMode(indicator_led_pin, OUTPUT);

	//--- Programming Pin ---
	pinMode(PGM_DO_pin, OUTPUT);
	
	//--- FPWM pins ---
	num_ports = sizeof(FPWM_pin)/sizeof(FPWM_pin[0]);
	for (uint8_t j = 0; j<num_ports; j++){
		num_pins = sizeof(FPWM_pin[j])/sizeof(FPWM_pin[j][0]);
		for (uint8_t i = 0; i<num_pins; i++){
			pinMode(FPWM_pin[j][i], OUTPUT);
		}
	}
	
	//--- Analogue pins ---
	num_ports = sizeof(Analog_pin)/sizeof(Analog_pin[0]);
	for (uint8_t j = 0; j<num_ports; j++){
		num_pins = sizeof(Analog_pin[j])/sizeof(Analog_pin[j][0]);
		for (uint8_t i = 0; i<num_pins; i++){
			pinMode(Analog_pin[j][i], INPUT);
		}	
	}
	
	//--- Analogue settings ---
	analogReadResolution(12);
	analogReadAveraging(32);
	analogWriteResolution(8);
	analogWriteFrequency(0, 1600);
	analogWriteFrequency(1, 1600);
	analogWriteFrequency(2, 1600);
	
	//--- Slow PWM driver ----
	spwm = PWMDriver(0x40);

	//--- Multiplexer pins ---
	num_pins = sizeof(I2C_MUL_ADR_pin)/sizeof(I2C_MUL_ADR_pin[0]);
	for (uint8_t i = 0; i<num_pins; i++){
		pinMode(I2C_MUL_ADR_pin[i], OUTPUT);
	}	

	//--- I2C initialization ----
	Wire.begin(I2C_MASTER,0x00, I2C_PINS_18_19, I2C_PULLUP_EXT, I2C_RATE_100);


}

TeensyUnit::~TeensyUnit(){

}

//===========================================================================
//===== INITIALIZATION =====
//===========================================================================

void TeensyUnit::init(){
	
	//----- Begin slow PWM driver ----
	spwm_init(1000);
	
	RawHIDCommunicator::init();
}

void TeensyUnit::spwm_init(uint16_t freq){

	//----- Begin slow PWM driver ----
	noInterrupts();
	spwm.begin();
	spwm.setPWMFreq(freq);  // This is the maximum PWM frequency
	interrupts();

}
