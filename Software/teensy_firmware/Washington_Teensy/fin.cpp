#include "fin.h"

//===========================================================================
//===== Washington Fin Node =====
//===========================================================================

WashingtonFinNode::WashingtonFinNode(uint8_t fin0_port_id,
                                     uint8_t fin1_port_id,
                                     uint8_t fin2_port_id,
                                     uint8_t light0_port_id,
                                     uint8_t light1_port_id,
                                     uint8_t light2_port_id
                                    ):
  FinsLightsUnit(fin0_port_id, fin1_port_id, fin2_port_id,
                 light0_port_id, light1_port_id, light2_port_id)
{

}

WashingtonFinNode::~WashingtonFinNode() {

}

void WashingtonFinNode::parse_msg() {


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
        // >>>>> byte 2 to byte 9: Fin 0
        // >>>>> byte 10 to byte 17: Fin 1
        // >>>>> byte 18 to byte 25: Fin 2


        for (uint8_t j = 0; j < WashingtonFinNode::NUM_FIN; j++) {

          const uint8_t byte_offset = 8 * (j) + device_offset;

          // byte x0 --- fin SMA wire 0
          fin_var[j].sma_level[0] = recv_data_buff[byte_offset + 0];
          // byte x1 --- fin SMA wire 1
          fin_var[j].sma_level[1] = recv_data_buff[byte_offset + 1];
          // byte x2 --- reflex actuation level
          fin_var[j].reflex_level[0] = recv_data_buff[byte_offset + 2];
          // byte x3 --- reflex actuation level
          fin_var[j].reflex_level[1] = recv_data_buff[byte_offset + 3];

        }

        device_offset += 8 * WashingtonFinNode::NUM_FIN;

        // (8 bytes each)
        // >>>>> byte 26 to byte 33: Light 0
        // >>>>> byte 34 to byte 41: Light 1
        // >>>>> byte 42 to byte 49: Light 2

        for (uint8_t j = 0; j < WashingtonFinNode::NUM_LIGHT; j++) {

          const uint8_t byte_offset = 8 * (j) + device_offset;

          // byte x0 --- LED 0 level
          light_var[j].led_level[0] = recv_data_buff[byte_offset + 0];
          // byte x1 --- LED 1 level
          light_var[j].led_level[1] = recv_data_buff[byte_offset + 1];
          // byte x2 --- LED 2 level
          light_var[j].led_level[2] = recv_data_buff[byte_offset + 2];
          // byte x3 --- LED 3 level
          light_var[j].led_level[3] = recv_data_buff[byte_offset + 3];

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


//====== COMMUNICATION Protocol ======

void WashingtonFinNode::compose_reply(byte front_signature, byte back_signature, byte msg_setting) {


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

        // >>>>> byte 2 to byte 15: FIN 0
        // >>>>> byte 16 to byte 29: FIN 1
        // >>>>> byte 30 to byte 43: FIN 2

        for (uint8_t j = 0; j < WashingtonFinNode::NUM_FIN; j++) {

          const uint8_t byte_offset = 14 * (j) + device_offset;

          // byte x0 --- IR 0 sensor state
          for (uint8_t i = 0; i < 2; i++)
            send_data_buff[byte_offset + 0 + i] = fin_var[j].ir_state[0] >> (8 * i);

          // byte x2 --- IR 1 sensor state
          for (uint8_t i = 0; i < 2; i++)
            send_data_buff[byte_offset + 2 + i] = fin_var[j].ir_state[1] >> (8 * i);


          // byte x4 -- Accelerometer state (x-axis)
          for (uint8_t i = 0; i < 2; i++)
            send_data_buff[byte_offset + 4 + i] = fin_var[j].acc_state[0] >> (8 * i);

          // byte x6 -- Accelerometer state (y-axis)
          for (uint8_t i = 0; i < 2; i++)
            send_data_buff[byte_offset + 6 + i] = fin_var[j].acc_state[1] >> (8 * i);

          // byte x8 -- Accelerometer state (z-axis)
          for (uint8_t i = 0; i < 2; i++)
            send_data_buff[byte_offset + 8 + i] = fin_var[j].acc_state[2] >> (8 * i);

          // byte x10 -- cycling
          send_data_buff[byte_offset + 10] = (uint8_t) fin_var[j].cycling;

        }

        device_offset = 14 * WashingtonFinNode::NUM_FIN + device_offset;

        // (4 bytes each)
        // >>>>> byte 44 to byte 47: LIGHT 0
        // >>>>> byte 48 to byte 51: LIGHT 1
        // >>>>> byte 52 to byte 55: LIGHT 2

        for (uint8_t j = 0; j < WashingtonFinNode::NUM_LIGHT; j++) {

          const uint8_t byte_offset = 4 * (j) + device_offset;

          // byte x0 --- IR 0 sensor state
          for (uint8_t i = 0; i < 2; i++)
            send_data_buff[byte_offset + 0 + i] = light_var[j].ir_state[0] >> (8 * i);
          // byte x2 --- IR 1 sensor state
          for (uint8_t i = 0; i < 2; i++)
            send_data_buff[byte_offset + 2 + i] = light_var[j].ir_state[1] >> (8 * i);


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

//====== Input functions ======

//--- Sampling function ---
void WashingtonFinNode::sample_inputs() {

  sample_inputs(0);
}

void WashingtonFinNode::sample_inputs(const uint8_t setting) {


  //=== Fin ===

  for (uint8_t j = 0; j < WashingtonFinNode::NUM_FIN; j++) {

    //~~IR sensors state~~
    for (uint8_t i = 0; i < 2; i++) {

      noInterrupts();
      fin_var[j].ir_state[i] = fin[j].read_analog_state(i);
      interrupts();

    }

    //~~Accelerometer~~
    noInterrupts();
    fin[j].read_acc_state(fin_var[j].acc_state[0],
                          fin_var[j].acc_state[1],
                          fin_var[j].acc_state[2]);

    interrupts();


  }
  //=== LIGHT ===

  for (uint8_t j = 0; j < WashingtonFinNode::NUM_LIGHT; j++) {

    //~~IR sensors state~~
    for (uint8_t i = 0; i < 2; i++) {

      noInterrupts();
      light_var[j].ir_state[i] = light[j].read_analog_state(i);
      interrupts();

    }

  }

}


//============ BEHAVIOUR CODES =========

//---- inactive behaviour ----
void WashingtonFinNode::inactive_behaviour() {


  //=== Fin ===
  for (uint8_t i = 0; i < WashingtonFinNode::NUM_FIN; i++) {

    fin[i].set_led_level(0, 0);
    fin[i].set_led_level(1, 0);

    fin[i].set_sma_level(0, 0);
    fin[i].set_sma_level(1, 0);

  }

  //=== Cricket ===
  for (uint8_t i = 0; i < WashingtonFinNode::NUM_LIGHT; i++) {

    for (uint8_t output_id = 0; output_id < 4; output_id++) {
      light[i].set_output_level(output_id, 0);
    }

  }

}

//---- test behaviour ----
void WashingtonFinNode::test_behaviour(const uint32_t &curr_time) {

  //---- Fin cycling variables -----
  static uint32_t high_level_ctrl_fin_phase_time[WashingtonFinNode::NUM_FIN] = {0, 0, 0};


  static uint8_t high_level_ctrl_sma0[WashingtonFinNode::NUM_FIN] = {0, 0, 0};
  static uint8_t high_level_ctrl_sma1[WashingtonFinNode::NUM_FIN] = {1, 1, 1};



  //~~~ fin cycle~~~~
  for (uint8_t j = 0; j < WashingtonFinNode::NUM_FIN; j++) {



    if (fin_var[j].motion_on < 1 && fin_var[j].cycling < 1) {

      fin[j].set_sma_level(0, 0);
      fin[j].set_sma_level(1, 0);
      fin_var[j].cycling  = 0;
      fin_var[j].motion_on = 3;
      continue;
    }


    // starting a cycle
    if (fin_var[j].cycling < 1) {

      // behaviour Type
      switch (fin_var[j].motion_on) {
        case 1:
          high_level_ctrl_sma0[j] = 0;
          high_level_ctrl_sma1[j] = 0;
          break;
        case 2:
          high_level_ctrl_sma0[j] = 1;
          high_level_ctrl_sma1[j] = 1;
          break;
        default:
          high_level_ctrl_sma0[j] = 0;
          high_level_ctrl_sma1[j] = 1;
          break;
      }
      fin_var[j].cycling = 1; //fin_var[j].motion_on;
      high_level_ctrl_fin_phase_time[j] = millis();

      // turn on the first sma
      fin[j].set_sma_level(high_level_ctrl_sma0[j], fin_var[j].sma_max_level[0]);
      fin[j].set_sma_level(high_level_ctrl_sma1[j],  fin_var[j].sma_max_level[1]);
    }
    else {


      volatile uint32_t cycle_time = curr_time - high_level_ctrl_fin_phase_time[j];

      // if reaches the full period, restart cycle
      if (cycle_time > ((fin_var[j].arm_cycle_period[1] + fin_var[j].arm_cycle_period[0]) * 100)) {
        fin_var[j].cycling  = 0;
        fin_var[j].motion_on = 0;
      }

      //if reaches the on period
      else if (cycle_time > (fin_var[j].arm_cycle_period[0] * 100)) {
        fin[j].set_sma_level(high_level_ctrl_sma1[j], 0);
        fin[j].set_sma_level(high_level_ctrl_sma0[j], 0);

      }

    }


  }




  //>>>> Fin <<<<<

  for (uint8_t j = 0; j < WashingtonFinNode::NUM_FIN; j++) {
    if (fin_var[j].ir_state[0] > 1200) {
      fin[j].set_led_level(0, 250);
      fin[j].set_led_level(1, 250);
      // fin[j].set_sma_level(0, 250);
      // fin[j].set_sma_level(1, 250);
    }
    else {
      fin[j].set_led_level(0, 0);
      fin[j].set_led_level(1, 0);
      // fin[j].set_sma_level(0, 0);
      // fin[j].set_sma_level(1, 0);
    }
  }

  //>>>> Light <<<<<

  for (uint8_t j = 0; j < WashingtonFinNode::NUM_LIGHT; j++) {
    if (light_var[j].ir_state[0] > 1200) {
      for (uint8_t output_id = 0; output_id < 4; output_id++) {
        light[j].set_output_level(output_id, 255);
      }
    }
    else {
      for (uint8_t output_id = 0; output_id < 4; output_id++) {
        light[j].set_output_level(output_id, 0);
      }

    }

  }

}

//---- self_running_behaviour ----
void WashingtonFinNode::self_running_behaviour(const uint32_t &curr_time) {
  //---- Fin cycling variables -----
  static uint32_t high_level_ctrl_fin_phase_time[WashingtonFinNode::NUM_FIN] = {0, 0, 0};
  static uint8_t high_level_ctrl_sma0[WashingtonFinNode::NUM_FIN] = {0, 0, 0};
  static uint8_t high_level_ctrl_sma1[WashingtonFinNode::NUM_FIN] = {1, 1, 1};

  //~~~ fin cycle~~~~
  for (uint8_t j = 0; j < WashingtonFinNode::NUM_FIN; j++) {

    if ((fin_var[j].ir_state[1] < 1200 && fin_var[j].ir_state[0] < 1200)
        && fin_var[j].cycling < 1) {

      fin[j].set_sma_level(0, 0);
      fin[j].set_sma_level(1, 0);
      fin_var[j].cycling  = 0;
      fin_var[j].motion_on = 3;
      continue;
    }

    // starting a cycle
    if (fin_var[j].cycling < 1) {

      // behaviour Type
      switch (fin_var[j].motion_on) {
        case 1:
          high_level_ctrl_sma0[j] = 0;
          high_level_ctrl_sma1[j] = 0;
          break;
        case 2:
          high_level_ctrl_sma0[j] = 1;
          high_level_ctrl_sma1[j] = 1;
          break;
        default:
          high_level_ctrl_sma0[j] = 0;
          high_level_ctrl_sma1[j] = 1;
          break;
      }
      fin_var[j].cycling = 1; //fin_var[j].motion_on;
      high_level_ctrl_fin_phase_time[j] = millis();

      // turn on the first sma
      fin[j].set_sma_level(high_level_ctrl_sma0[j], fin_var[j].sma_max_level[0]);
      fin[j].set_sma_level(high_level_ctrl_sma1[j],  fin_var[j].sma_max_level[1]);
    }
    else {

      volatile uint32_t cycle_time = curr_time - high_level_ctrl_fin_phase_time[j];

      // if reaches the full period, restart cycle
      if (cycle_time > ((fin_var[j].arm_cycle_period[1] + fin_var[j].arm_cycle_period[0]) * 100)) {
        fin_var[j].cycling  = 0;
        fin_var[j].motion_on = 0;
      }

      //if reaches the on period
      else if (cycle_time > (fin_var[j].arm_cycle_period[0] * 100)) {
        fin[j].set_sma_level(high_level_ctrl_sma1[j], 0);
        fin[j].set_sma_level(high_level_ctrl_sma0[j], 0);
      }
    }
  }


  //>>>> Fin Light <<<<<
  static uint8_t motor_max_level = 150;

  static uint8_t light_max_level = 255;
  for (uint8_t j = 0; j < WashingtonFinNode::NUM_FIN; j++) {

    // starting a cycle
    if (fin_var[j].ir_state[0] > 1200
        && !fin_var[j].reflex_cycling) {
      Serial.println("starting cycle");
      fin_var[j].reflex_cycling = true;
      fin_var[j].reflex_phase_time = millis();
      fin_var[j].reflex_step_time = millis();
      fin_var[j].reflex_next_step_time = 2;
    }
    else if (fin_var[j].reflex_cycling) {

      volatile uint32_t cycle_time = curr_time - fin_var[j].reflex_phase_time;

      //ramping down
      // if reaches the full period, restart cycle
      if (cycle_time > 1500) {

        volatile uint32_t ramping_time = curr_time - fin_var[j].reflex_step_time;

        if (ramping_time > fin_var[j].reflex_next_step_time) {
          for (uint8_t output_id = 0; output_id < 2; output_id++) {
            if (fin_var[j].reflex_level[output_id] > 0)
              fin_var[j].reflex_level[output_id] -= 1;
          }
          fin_var[j].reflex_next_step_time += 1;
          fin_var[j].reflex_step_time = millis();
        }

        bool end_cycling = true;
        for (uint8_t output_id = 0; output_id < 2; output_id++) {
          end_cycling &= fin_var[j].reflex_level[output_id] <= 0 ;
        }
        if (end_cycling) {
          fin_var[j].reflex_cycling = 0;
        }

      }
      //hold steady
      else if (cycle_time > 1000) {

      }
      // ramping up
      else {
        volatile uint32_t ramping_time = curr_time - fin_var[j].reflex_step_time;

        if (ramping_time > fin_var[j].reflex_next_step_time) {

          if (fin_var[j].reflex_level[0] < light_max_level)
            fin_var[j].reflex_level[0] += 1;
          if (fin_var[j].reflex_level[1] < motor_max_level)
            fin_var[j].reflex_level[1] += 1;

          fin_var[j].reflex_next_step_time += 1;
          fin_var[j].reflex_step_time = millis();
        }

      }
    }
  }





}

//---- indicator LED -----

void WashingtonFinNode::led_blink_behaviour(const uint32_t &curr_time) {

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
void WashingtonFinNode::low_level_control_behaviour(const uint32_t &curr_time) {


  //>>>> FIN <<<<<
  for (uint8_t j = 0; j < WashingtonFinNode::NUM_FIN; j++) {


    //sma protection mechanism
    if (fin_var[j].sma_level[0] > fin_var[j].sma_max_level[0])
      fin_var[j].sma_level[0] =  fin_var[j].sma_max_level[0];
    if (fin_var[j].sma_level[1] > fin_var[j].sma_max_level[1])
      fin_var[j].sma_level[1] =  fin_var[j].sma_max_level[1];

    fin[j].set_sma_level(0, fin_var[j].sma_level[0]);
    fin[j].set_sma_level(1, fin_var[j].sma_level[1]);
    fin[j].set_led_level(0, fin_var[j].reflex_level[0]);
    fin[j].set_led_level(1, fin_var[j].reflex_level[1]);


  }

  //>>>> Light <<<<<

  for (uint8_t j = 0; j < WashingtonFinNode::NUM_LIGHT; j++) {

    for (uint8_t output_id = 0; output_id < 4; output_id++) {
      light[j].set_output_level(output_id, light_var[j].led_level[output_id]);
    }

  }
}
