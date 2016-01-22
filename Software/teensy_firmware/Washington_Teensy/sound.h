#ifndef _SOUND_H
#define _SOUND_H

#include "sounds_unit.h"

class SoundUnitVar{

	private:
	
		friend class WashingtonSoundNode;
	
		//----INPUT----
		
		//~~Analog state~~
		uint16_t analog_state[3] = {0, 0, 0};
		
	
		//----OUTPUT----
		
		bool digital_trigger[2] = {0, 0};
		uint8_t output_level[2] = {0, 0};
		
		uint8_t sound_type[2] = {0, 0}; // 0 = off
		uint8_t sound_volume[2] = {0, 0}; // 0 = 0%, 50 = 100%, 100 = 200%
		uint8_t sound_block[2] = {0, 0};
};

class WashingtonSoundNode : public SoundsUnit{

  public:
    
    //===============================================
    //==== Constructor and destructor =====
    //===============================================
    
    WashingtonSoundNode(uint8_t sound0_port_id, 
              uint8_t sound1_port_id, 
              uint8_t sound2_port_id,
              uint8_t sound3_port_id, 
              uint8_t sound4_port_id, 
              uint8_t sound5_port_id
                );
    ~WashingtonSoundNode();

    //===============================================
    //==== Communication functions =====
    //===============================================
      
    void parse_msg();
    void compose_reply(byte front_signature, byte back_signature, byte msg_setting);
    
    //--- Input functions----
    void sample_inputs();
    void sample_inputs(const uint8_t setting);
    
    //===============================================
    //==== BEHAVIOUR functions =====
    //===============================================
    
    //---- inactive behaviour ----
    void inactive_behaviour();
    
    //---- test behaviour ----
    void test_behaviour(const uint32_t &curr_time);
    
    //---- self-running behaviour ----
    void self_running_behaviour(const uint32_t &curr_time);
    
    //---- indicator LED -----
    void led_blink_behaviour(const uint32_t &curr_time);
  
    //---- low-level control ---
    void low_level_control_behaviour(const uint32_t &curr_time);

    
    //===============================================
    //==== BEHAVIOUR variables =====
    //=============================================== 
    
    //>>> Teensy on-board <<<<
    
    //----OUTPUT----
    //~~indicator LED on~~
    bool indicator_led_on = false; 
    //~~indicator LED blink~~
    uint16_t indicator_led_blink_period = 1000; 
    
    //~~operation mode~~~
    uint8_t operation_mode = 0;

    //>>> Sound <<<
    SoundUnitVar sound_var[WashingtonSoundNode::NUM_SOUND];
    // bool play_started_L[4] = {false, false, false, false};
    // bool play_started_R[4] = {false, false, false, false};
    
    //>>> Network Activities <<<
    
    //----OUTPUT (internal variables)----
    uint8_t neighbour_activation_state = 0;
    
  
  private:  
};


#endif
