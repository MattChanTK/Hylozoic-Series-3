#include "sound.h"

//===========================================================================
//===== Washington Sound Node =====
//===========================================================================

WashingtonSoundNode::WashingtonSoundNode(uint8_t sound0_port_id,
    uint8_t sound1_port_id,
    uint8_t sound2_port_id,
    uint8_t sound3_port_id,
    uint8_t sound4_port_id,
    uint8_t sound5_port_id
                                        ):
  SoundsUnit(sound0_port_id, sound1_port_id, sound2_port_id,
             sound3_port_id, sound4_port_id, sound5_port_id)
{

}

WashingtonSoundNode::~WashingtonSoundNode() {

}

void WashingtonSoundNode::parse_msg() {


  // byte 1 --- type of request
  request_type = recv_data_buff[1];


  uint16_t temp_val = 0;

  switch (request_type) {

    // Basic
    case 0: {

        // >>>>>> byte 2 to 9: ON-BOARD <<<<<<<

        // byte 2 --- indicator led on or off
        indicator_led_on = recv_data_buff[2];

        // byte 3 and 4 --- indicator led blinking frequency
        temp_val = 0;
        for (uint8_t i = 0; i < 2 ; i++)
          temp_val += recv_data_buff[3 + i] << (8 * i);
        indicator_led_blink_period = temp_val;

        // >>>> byte 10: CONFIG VARIABLES <<<<<

        // byte 10 ---- operation mode
        operation_mode = recv_data_buff[10];

        // byte 11 ---- reply message type request
        reply_type = recv_data_buff[11];

        // >>>>> byte 30 to byte 39:
        neighbour_activation_state = recv_data_buff[30];

        break;
      }

    //Teensy programming pin
    case 1: {

        bool program_teensy = recv_data_buff[2];

        if (program_teensy) {
          digitalWrite(PGM_DO_pin, 1);
          digitalWrite(13, 1);
        }

        break;
      }

    //low level requests
    case 2: {

        uint8_t  device_offset = 2;

        // (8 bytes each)
        // >>>>> byte 2 to byte 9: Sound 0
        // >>>>> byte 10 to byte 17: Sound 1
        // >>>>> byte 18 to byte 25: Sound 2
        // >>>>> byte 26 to byte 33: Sound 3
        // >>>>> byte 34 to byte 41: Sound 4
        // >>>>> byte 42 to byte 49: Sound 5


        for (uint8_t j = 0; j < WashingtonSoundNode::NUM_SOUND; j++) {

          const uint8_t byte_offset = 8 * (j) + device_offset;

          // byte x0 --- sound PWM output 0
          sound_var[j].output_level[0] = recv_data_buff[byte_offset + 0];
          // byte x1 --- sound PWM output 1
          sound_var[j].output_level[1] = recv_data_buff[byte_offset + 1];

          // byte x2 --- sound type left
          sound_var[j].sound_type[0] = recv_data_buff[byte_offset + 2];
          // byte x3 --- sound type right
          sound_var[j].sound_type[1] = recv_data_buff[byte_offset + 3];

          // byte x4 --- sound volume left
          sound_var[j].sound_volume[0] = recv_data_buff[byte_offset + 4];
          // byte x5 --- sound volume right
          sound_var[j].sound_volume[1] = recv_data_buff[byte_offset + 5];

          // byte x6 --- sound block left
          sound_var[j].sound_block[0] = recv_data_buff[byte_offset + 6];
          // byte x7 --- sound block right
          sound_var[j].sound_block[1] = recv_data_buff[byte_offset + 7];
        }

      }

    // read-only
    case 255: {
        break;
      }
    default: {
        break;
      }


  }

}


//===========================================================================
//====== COMMUNICATION Protocol ======
//===========================================================================

void WashingtonSoundNode::compose_reply(byte front_signature, byte back_signature, byte msg_setting) {


  // add the signatures to first and last byte
  send_data_buff[0] = front_signature;
  send_data_buff[num_outgoing_byte - 1] = back_signature;

  if (msg_setting == 0) {
    // sample the sensors
    this->sample_inputs();
  }

  // add the signatures to first and last byte
  send_data_buff[0] = front_signature;
  send_data_buff[num_outgoing_byte - 1] = back_signature;

  if (msg_setting == 0) {
    // sample the sensors
    this->sample_inputs();
  }

  // byte 1 --- type of reply
  send_data_buff[1] =  reply_type;


  switch (reply_type) {

    case 0:	{

        uint8_t  device_offset = 2;

        // >>>>> byte 2 to byte 9: Sound 0
        // >>>>> byte 10 to byte 17: Sound 1
        // >>>>> byte 18 to byte 25: Sound 2
        // >>>>> byte 26 to byte 33: Sound 3
        // >>>>> byte 34 to byte 41: Sound 4
        // >>>>> byte 42 to byte 49: Sound 5
        for (uint8_t j = 0; j < WashingtonSoundNode::NUM_SOUND; j++) {

          const uint8_t byte_offset = 8 * (j) + device_offset;

          // byte x0 --- IR 0 sensor state
          for (uint8_t i = 0; i < 2; i++)
            send_data_buff[byte_offset + 0 + i] = sound_var[j].analog_state[0] >> (8 * i);

          // byte x2 --- IR 1 sensor state
          for (uint8_t i = 0; i < 2; i++)
            send_data_buff[byte_offset + 2 + i] = sound_var[j].analog_state[1] >> (8 * i);

          // byte x4 --- IR 2 sensor state
          for (uint8_t i = 0; i < 2; i++)
            send_data_buff[byte_offset + 4 + i] = sound_var[j].analog_state[2] >> (8 * i);

        }

        break;


      }

    // echo
    case 1: {

        for (uint8_t i = 2; i < 63; i++) {

          send_data_buff[i] = recv_data_buff[i];
        }
        break;

      }
    default: {
        break;
      }

  }




}

//===========================================================================
//====== Input functions ======
//===========================================================================

//--- Sampling function ---
void WashingtonSoundNode::sample_inputs() {

  sample_inputs(0);
}

void WashingtonSoundNode::sample_inputs(const uint8_t setting) {


  //=== Sound ===

  for (uint8_t j = 0; j < WashingtonSoundNode::NUM_SOUND; j++) {

    //~~Analog inputs~~
    // noInterrupts();
    sound[j].read_analog_state(sound_var[j].analog_state[0],
                               sound_var[j].analog_state[1],
                               sound_var[j].analog_state[2]);

    // interrupts();


  }


}



//===========================================================================
//============ BEHAVIOUR CODES =========
//===========================================================================

//---- inactive behaviour ----
void WashingtonSoundNode::inactive_behaviour() {


  //=== Sound ===
  for (uint8_t j = 0; j < WashingtonSoundNode::NUM_SOUND; j++) {

    for (uint8_t i = 0; i < 2; i++) {
      sound[j].set_output_level(i, 0);
    }
    for (uint8_t i = 0; i < 2; i++) {
      sound[j].set_digital_trigger(i, false);
    }

  }

}

//---- test behaviour ----
void WashingtonSoundNode::test_behaviour(const uint32_t &curr_time) {

  static int song_id = 1;

  for (uint8_t j = 0; j < WashingtonSoundNode::NUM_SOUND; j++) {
    Serial.println(sound_var[j].analog_state[0]);
    if (sound_var[j].analog_state[0] > 1200) {
      Serial.println(song_id);

      sound[j].set_output_level(0, 100);
      sound[j].play_sound(song_id,  10, 2, 0, true);
      song_id += 1;
      if (song_id > 4) {
        song_id = 1;
      }

    }
    else {
      sound[j].set_output_level(0, 0);

    }

    if (sound_var[j].analog_state[1] > 1200) {
      sound[j].set_output_level(1, 100);
      sound[j].play_sound(2, 10, 1, 0, true);
    }
    else {

      sound[j].set_output_level(1, 0);

    }


  }

}

//---- self_running_behaviour ----
void WashingtonSoundNode::self_running_behaviour(const uint32_t &curr_time) {
  // low_level_control_behaviour(curr_time);
  test_behaviour(curr_time);
}

//---- indicator LED -----

void WashingtonSoundNode::led_blink_behaviour(const uint32_t &curr_time) {

  //---- indicator LED blinking variables -----
  //~~indicator LED on~~
  //static bool indicator_led_on_0 = 1;
  //~~indicator LED blink~~
  static bool indicator_led_blink_cycling = false;
  static uint32_t indicator_led_blink_phase_time = 0;

  if (indicator_led_on) {

    // starting a blink cycle
    if (indicator_led_blink_cycling == false) {
      indicator_led_blink_cycling = true;
      indicator_led_blink_phase_time = millis();
      digitalWrite(indicator_led_pin, 1);
    }
    else if (indicator_led_blink_cycling == true) {

      // if reaches the full period, restart cycle
      if ((curr_time - indicator_led_blink_phase_time) > indicator_led_blink_period) {
        indicator_led_blink_cycling = false;
      }
      // if reaches half the period, turn it off
      else if ((curr_time - indicator_led_blink_phase_time) > indicator_led_blink_period >> 1) {
        digitalWrite(indicator_led_pin, 0);
      }
    }
  }
  else {

    // if stopped in the middle of a cycle
    indicator_led_blink_cycling = false;

    digitalWrite(indicator_led_pin, 0);
  }
}



//----- LOW-LEVEL CONTROL -------
void WashingtonSoundNode::low_level_control_behaviour(const uint32_t &curr_time) {

  //>>>> PWM <<<<<
  for (uint8_t j = 0; j < WashingtonSoundNode::NUM_SOUND; j++) {

    sound[j].set_output_level(0, sound_var[j].output_level[0]);
    sound[j].set_output_level(1, sound_var[j].output_level[1]);
  }

  //>>>> Sound <<<<<
  for (uint8_t j = 0; j < WashingtonSoundNode::NUM_SOUND; j++) {

    for (uint8_t channel = 0; channel < 2; channel++) {
      if (sound_var[j].sound_type[channel]) {
        sound[j].play_sound(sound_var[j].sound_type[channel],
                            sound_var[j].sound_volume[channel],
                            channel, 0,
                            sound_var[j].sound_block[channel] > 0);
      }

    }

  }

}
