#include "teensy_unit.h"

//===========================================================================
//===== CONSTRUCTOR and DECONSTRUCTOR =====
//===========================================================================

TeensyUnit::TeensyUnit():
	FPWM_pin {FPWM_1_pin, FPWM_2_pin, FPWM_3_pin, FPWM_4_pin, FPWM_5_pin, FPWM_6_pin},
	SPWM_pin {SPWM_1_pin, SPWM_2_pin, SPWM_3_pin, SPWM_4_pin, SPWM_5_pin, SPWM_6_pin}, 
	Analog_pin {Analog_1_pin, Analog_2_pin, Analog_3_pin, Analog_4_pin, Analog_5_pin, Analog_6_pin},
	tentacle_0(*this, 0, false), 
	tentacle_1(*this, 1, false),
	tentacle_2(*this, 2, true)
	
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
	
	//--- Multiplexer pins ---
	num_pins = sizeof(MUL_ADR_pin)/sizeof(MUL_ADR_pin[0]);
	for (uint8_t i = 0; i<num_pins; i++){
		pinMode(MUL_ADR_pin[i], OUTPUT);
	}	
	
	
	
	
}

TeensyUnit::~TeensyUnit(){

}

//===========================================================================
//===== INITIALIZATION =====
//===========================================================================

void TeensyUnit::init(){

	//===== clear all existing messages ======
	unsigned long clearing_counter = 0;
	while (receive_msg()){
	    // this prevents the Teensy from being stuck in infinite loop
	    clearing_counter++;
	    if (clearing_counter>10000000){
			break;
        }
		
	}
	

}



//===========================================================================
//====== COMMUNICATION ======
//===========================================================================

bool TeensyUnit::receive_msg(){

	noInterrupts();
	uint8_t byteCount = 0;
	byteCount = RawHID.recv(recv_data_buff, 0);
	interrupts();

	if (byteCount > 0) {
		
		
		// extract the front and end signatures
		byte front_signature = recv_data_buff[0];
		byte back_signature = recv_data_buff[num_incoming_byte-1];

		// compose reply message
		this->compose_reply(front_signature, back_signature);
		send_msg();
		return true;
	}
	else{
		return false;
	}
}

void TeensyUnit::send_msg(){

	// Send a message
	noInterrupts();
	RawHID.send(send_data_buff, 10);
	interrupts();
}



//===========================================================================
//====== Tentacle Port ======
//===========================================================================
//~~constructor and destructor~~
TeensyUnit::TentaclePort::TentaclePort(TeensyUnit& teensy_parent, const uint8_t Port_Id, const bool All_Slow):
			teensy_unit(teensy_parent),
			port_id(Port_Id),
			is_all_slow(All_Slow)
			
{
	
	//----- Pin assignment -----
	spwm = PWMDriver(0x40),
	sma_pins[0] = teensy_unit.SPWM_pin[port_id][0];
	sma_pins[1] = teensy_unit.SPWM_pin[port_id][1];
	
	if (is_all_slow){
		led_pins[0] = teensy_unit.SPWM_pin[port_id][2];
		led_pins[1] = teensy_unit.SPWM_pin[port_id][3];
	}
	else{
		led_pins[0] = teensy_unit.FPWM_pin[port_id][0];
		led_pins[1] = teensy_unit.FPWM_pin[port_id][1];
	}
	
	analog_pins[0] = teensy_unit.Analog_pin[port_id][0];
	analog_pins[1] = teensy_unit.Analog_pin[port_id][1];
	
	
	//----- Begin slow PWM driver ----
	spwm_init(1000);
	
}

TeensyUnit::TentaclePort::~TentaclePort(){
	
}

void TeensyUnit::TentaclePort::spwm_init(uint16_t freq){
	//----- Begin slow PWM driver ----
	spwm.begin();
	spwm.setPWMFreq(freq);  // This is the maximum PWM frequency
	
}

//~~outputs~~
void TeensyUnit::TentaclePort::set_sma_level(const uint8_t id, const uint8_t level){

	spwm.setPWMFast(sma_pins[id], 16*level);
	
}
void TeensyUnit::TentaclePort::set_led_level(const uint8_t id, const uint8_t level){

	if (is_all_slow){
		spwm.setPWMFast(led_pins[id], 16*level);
	}
	else{
		analogWrite(led_pins[id], level);
	}
}

//~~inputs~~
uint16_t TeensyUnit::TentaclePort::read_analog_state(const uint8_t id){  //{IR 0, IR 1}
	return (uint16_t) analogRead(analog_pins[id]);
}

uint16_t* TeensyUnit::TentaclePort::read_acc_state(){ // return array:{x, y, z}

}
				
