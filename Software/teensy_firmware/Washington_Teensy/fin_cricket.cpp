#define FIN_DECAY_THRESHOLD 0.8

#include "Arduino.h"

#include "fin_cricket.h"

//===========================================================================
//===== Washington Fin Cricket Node =====
//===========================================================================

WashingtonFinCricketNode::WashingtonFinCricketNode(uint8_t fin0_port_id,
    uint8_t fin1_port_id,
    uint8_t fin2_port_id,
    uint8_t cricket0_port_id,
    uint8_t cricket1_port_id,
    uint8_t cricket2_port_id
                                                  ):
  FinsCricketsUnit(fin0_port_id, fin1_port_id, fin2_port_id,
                   cricket0_port_id, cricket1_port_id, cricket2_port_id)
{

}

WashingtonFinCricketNode::~WashingtonFinCricketNode() {

}

void WashingtonFinCricketNode::parse_msg() {


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

    //Crickets low level requests
    case 2: {

        uint8_t  device_offset = 2;

        // (8 bytes each)
        // >>>>> byte 2 to byte 9: Fin 0
        // >>>>> byte 10 to byte 17: Fin 1
        // >>>>> byte 18 to byte 25: Fin 2


        for (uint8_t j = 0; j < WashingtonFinCricketNode::NUM_FIN; j++) {

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

        device_offset += 8 * WashingtonFinCricketNode::NUM_FIN;

        // (8 bytes each)
        // >>>>> byte 26 to byte 33: Cricket 0
        // >>>>> byte 34 to byte 41: Cricket 1
        // >>>>> byte 42 to byte 49: Cricket 2

        for (uint8_t j = 0; j < WashingtonFinCricketNode::NUM_CRICKET; j++) {

          const uint8_t byte_offset = 8 * (j) + device_offset;

          // byte x0 --- actuator 0 level
          cricket_var[j].output_level[0] = recv_data_buff[byte_offset + 0];
          // byte x1 --- actuator 1 level
          cricket_var[j].output_level[1] = recv_data_buff[byte_offset + 1];
          // byte x2 --- actuator 2 level
          cricket_var[j].output_level[2] = recv_data_buff[byte_offset + 2];
          // byte x3 --- actuator 3 level
          cricket_var[j].output_level[3] = recv_data_buff[byte_offset + 3];

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

void WashingtonFinCricketNode::compose_reply(byte front_signature, byte back_signature, byte msg_setting) {


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

        for (uint8_t j = 0; j < WashingtonFinCricketNode::NUM_FIN; j++) {

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

        device_offset = 14 * WashingtonFinCricketNode::NUM_FIN + device_offset;

        // (4 bytes each)
        // >>>>> byte 44 to byte 47: Cricket 0
        // >>>>> byte 48 to byte 51: Cricket 1
        // >>>>> byte 52 to byte 55: Cricket 2

        for (uint8_t j = 0; j < WashingtonFinCricketNode::NUM_CRICKET; j++) {

          const uint8_t byte_offset = 4 * (j) + device_offset;

          // byte x0 --- IR 0 sensor state
          for (uint8_t i = 0; i < 2; i++)
            send_data_buff[byte_offset + 0 + i] = cricket_var[j].ir_state >> (8 * i);


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
void WashingtonFinCricketNode::sample_inputs() {

  sample_inputs(0);
}

void WashingtonFinCricketNode::sample_inputs(const uint8_t setting) {


  //=== Fin ===

  for (uint8_t j = 0; j < WashingtonFinCricketNode::NUM_FIN; j++) {

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
  //=== Cricket ===
  for (uint8_t j = 0; j < WashingtonFinCricketNode::NUM_CRICKET; j++) {

    //~~IR sensors state~~
    noInterrupts();
    cricket_var[j].ir_state = cricket[j].read_analog_state(0);
    interrupts();

  }

}



//============ BEHAVIOUR CODES =========

//---- inactive behaviour ----
void WashingtonFinCricketNode::inactive_behaviour() {


  //=== Fin ===
  for (uint8_t i = 0; i < WashingtonFinCricketNode::NUM_FIN; i++) {

    fin[i].set_led_level(0, 0);
    fin[i].set_led_level(1, 0);

    fin[i].set_sma_level(0, 0);
    fin[i].set_sma_level(1, 0);

  }

  //=== Cricket ===
  for (uint8_t i = 0; i < WashingtonFinCricketNode::NUM_CRICKET; i++) {

    for (uint8_t output_id = 0; output_id < 4; output_id++) {
      cricket[i].set_output_level(output_id, 0);
    }

  }

}

//---- test behaviour ----
void WashingtonFinCricketNode::test_behaviour(const uint32_t &curr_time) {

  //---- Fin cycling variables -----
  static uint32_t high_level_ctrl_fin_phase_time[WashingtonFinCricketNode::NUM_FIN] = {0, 0, 0};


  static uint8_t high_level_ctrl_sma0[WashingtonFinCricketNode::NUM_FIN] = {0, 0, 0};
  static uint8_t high_level_ctrl_sma1[WashingtonFinCricketNode::NUM_FIN] = {1, 1, 1};



  //~~~ fin cycle~~~~
  for (uint8_t j = 0; j < WashingtonFinCricketNode::NUM_FIN; j++) {

    // Update the average fin values
    for( int i=0; i<2; i++){
      fin_var[j].ir_averages[i].add(fin_var[j].ir_state[i]);
    }

    // Tests current value against average and decaying maximums
    if ((fin_var[j].ir_averages[1].decay_fraction(fin_var[j].ir_state[1]) < FIN_DECAY_THRESHOLD
        && fin_var[j].ir_averages[0].decay_fraction(fin_var[j].ir_state[0]) < FIN_DECAY_THRESHOLD)
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

  //>>>> Fin <<<<<

  for (uint8_t j = 0; j < WashingtonFinCricketNode::NUM_FIN; j++) {
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

  //>>>> Cricket <<<<<

  for (uint8_t j = 0; j < WashingtonFinCricketNode::NUM_CRICKET; j++) {
    if (cricket_var[j].ir_state > 1200) {
      for (uint8_t output_id = 0; output_id < 4; output_id++) {
        cricket[j].set_output_level(output_id, 100);
      }
    }
    else {
      for (uint8_t output_id = 0; output_id < 4; output_id++) {
        cricket[j].set_output_level(output_id, 0);
      }

    }

  }

}

//---- self_running_behaviour ----
void WashingtonFinCricketNode::self_running_behaviour(const uint32_t &curr_time) {


  //---- Fin cycling variables -----
  static uint32_t high_level_ctrl_fin_phase_time[WashingtonFinCricketNode::NUM_FIN] = {0, 0, 0};


  static uint8_t high_level_ctrl_sma0[WashingtonFinCricketNode::NUM_FIN] = {0, 0, 0};
  static uint8_t high_level_ctrl_sma1[WashingtonFinCricketNode::NUM_FIN] = {1, 1, 1};




  //~~~ fin cycle~~~~
  for (uint8_t j = 0; j < WashingtonFinCricketNode::NUM_FIN; j++) {


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
  for (uint8_t j = 0; j < WashingtonFinCricketNode::NUM_FIN; j++) {

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

  for (uint8_t j = 0; j < WashingtonFinCricketNode::NUM_FIN; j++) {
    fin[j].set_led_level(0, fin_var[j].reflex_level[0]);
    fin[j].set_led_level(1, fin_var[j].reflex_level[1]);
  }

  static const uint16_t cricket_max_level = 150;

  //>>>> Cricket <<<<<
  for (uint8_t j = 0; j < WashingtonFinCricketNode::NUM_CRICKET; j++) {

    // starting a cycle
    if (cricket_var[j].ir_state > 1200 && !cricket_var[j].cycling) {
      Serial.println("starting cycle");
      cricket_var[j].cycling = true;
      cricket_var[j].phase_time = millis();
      cricket_var[j].step_time = millis();
      cricket_var[j].next_step_time = 1;
    }
    else if (cricket_var[j].cycling) {

      volatile uint32_t cycle_time = curr_time - cricket_var[j].phase_time;

      //ramping down
      // if reaches the full period, restart cycle
      if (cycle_time > 4000) {

        volatile uint32_t ramping_time = curr_time - cricket_var[j].step_time;

        if (ramping_time > cricket_var[j].next_step_time) {
          for (uint8_t output_id = 0; output_id < 4; output_id++) {
            if (cricket_var[j].output_level[output_id] > 0)
              cricket_var[j].output_level[output_id] -= 1;
          }
          cricket_var[j].next_step_time += 1;
          cricket_var[j].step_time = millis();
        }

        bool end_cycling = true;
        for (uint8_t output_id = 0; output_id < 4; output_id++) {
          end_cycling &= cricket_var[j].output_level[output_id] <= 0 ;
        }
        if (end_cycling) {
          cricket_var[j].cycling = 0;
        }

      }
      //hold steady
      else if (cycle_time > 3000) {

      }
      // ramping up
      else {
        volatile uint32_t ramping_time = curr_time - cricket_var[j].step_time;

        if (ramping_time > cricket_var[j].next_step_time) {
          for (uint8_t output_id = 0; output_id < 4; output_id++) {
            if (cricket_var[j].output_level[output_id] < cricket_max_level)
              cricket_var[j].output_level[output_id] += 1;
          }
          if (cricket_var[j].output_level[0] < cricket_max_level)
            cricket_var[j].output_level[0] += 1;

          if (cycle_time > 500) {
            if (cricket_var[j].output_level[1] < cricket_max_level)
              cricket_var[j].output_level[1] += 1;
          }
          if (cycle_time > 1000) {
            if (cricket_var[j].output_level[2] < cricket_max_level)
              cricket_var[j].output_level[2] += 1;
          }
          if (cycle_time > 1500) {
            if (cricket_var[j].output_level[3] < cricket_max_level)
              cricket_var[j].output_level[3] += 1;
          }
          cricket_var[j].next_step_time += 1;
          cricket_var[j].step_time = millis();
        }

      }
    }
  }


  //>>>> Cricket <<<<<
  for (uint8_t j = 0; j < WashingtonCricketNode::NUM_CRICKET; j++) {

    for (uint8_t output_id = 0; output_id < 4; output_id++) {
      // Serial.print("c");
      // Serial.print(j);
      // Serial.print(".motor");
      // Serial.print(output_id);
      // Serial.print(": ");
      // Serial.println(cricket_var[j].output_level[output_id]);
      cricket[j].set_output_level(output_id, cricket_var[j].output_level[output_id]);
    }
  }




}

//---- indicator LED -----

void WashingtonFinCricketNode::led_blink_behaviour(const uint32_t &curr_time) {

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
void WashingtonFinCricketNode::low_level_control_behaviour(const uint32_t &curr_time) {

  //>>>> FIN <<<<<
  for (uint8_t j = 0; j < WashingtonFinCricketNode::NUM_FIN; j++) {


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


  //>>>> Cricket <<<<<

  for (uint8_t j = 0; j < WashingtonFinCricketNode::NUM_CRICKET; j++) {

    for (uint8_t output_id = 0; output_id < 4; output_id++) {
      cricket[j].set_output_level(output_id, cricket_var[j].output_level[output_id]);
    }

  }
}
