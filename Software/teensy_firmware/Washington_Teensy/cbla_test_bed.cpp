#include "cbla_test_bed.h"


//===========================================================================
//===== CONSTRUCTOR and DECONSTRUCTOR =====
//===========================================================================

CBLATestBed::CBLATestBed():
  FinsSingleLightsUnit(0, 1, 2, 3, 4, 5)
{

}

CBLATestBed::~CBLATestBed() {

}

void CBLATestBed::parse_msg() {


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

    //Fins high level requests
    case 2: {

        uint8_t  device_offset = 2;

        // (14 bytes each)
        // >>>>> byte 2 to byte 15: FIN 0
        // >>>>> byte 16 to byte 29: FIN 1
        // >>>>> byte 30 to byte 43: FIN 2

        for (uint8_t j = 0; j < NUM_FIN; j++) {

          const uint8_t byte_offset = 14 * (j) + device_offset;

          //--- internal variables---

          // byte x0 --- IR sensor 0 activation threshold
          temp_val = 0;
          for (uint8_t i = 0; i < wave_size; i++)
            temp_val += recv_data_buff[byte_offset + i + 0] << (8 * i);
          fin_var[j].ir_threshold[0] = temp_val;

          // byte x2 --- IR sensor 1 activation threshold
          temp_val = 0;
          for (uint8_t i = 0; i < wave_size; i++)
            temp_val += recv_data_buff[byte_offset + i + 2] << (8 * i);
          fin_var[j].ir_threshold[1] = temp_val;

          // byte x4 --- ON period of Fin arm activation
          fin_var[j].arm_cycle_period[0] = recv_data_buff[byte_offset + 4];

          // byte x5 --- OFF period of Fin arm activation
          fin_var[j].arm_cycle_period[1] = recv_data_buff[byte_offset + 5];

          // byte x6 --- Reflex channel 1 period
          temp_val = 0;
          for (uint8_t i = 0; i < wave_size; i++)
            temp_val += recv_data_buff[byte_offset + i + 6] << (8 * i);
          fin_var[j].reflex_period[0] = temp_val;

          // byte x8 --- Reflex channel 2 period
          temp_val = 0;
          for (uint8_t i = 0; i < wave_size; i++)
            temp_val += recv_data_buff[byte_offset + i + 8] << (8 * i);
          fin_var[j].reflex_period[1] = temp_val;


          //--- actuator output variables---

          // byte x10 --- fin motion activation
          fin_var[j].motion_on = recv_data_buff[byte_offset + 10];

          // byte x11 --- reflex channel 1 wave type
          fin_var[j].reflex_wave_type[0] = recv_data_buff[byte_offset + 11];

          // byte x12 --- reflex channel 2 wave type
          fin_var[j].reflex_wave_type[1] = recv_data_buff[byte_offset + 12];


        }
        break;
      }

    // Fins low level requests
    case 3: {

        uint8_t  device_offset = 2;

        // (14 bytes each)
        // >>>>> byte 2 to byte 15: FIN 0
        // >>>>> byte 16 to byte 29: FIN 1
        // >>>>> byte 30 to byte 43: FIN 2

        for (uint8_t j = 0; j < NUM_FIN; j++) {

          const uint8_t byte_offset = 14 * (j) + device_offset;

          // byte x0 --- fin SMA wire 0
          fin_var[j].sma_level[0] = recv_data_buff[byte_offset + 0];
          // byte x1 --- fin SMA wire 1
          fin_var[j].sma_level[1] = recv_data_buff[byte_offset + 1];
          // byte x2 --- reflex actuation level
          fin_var[j].reflex_level[0] = recv_data_buff[byte_offset + 2];
          // byte x4 --- reflex actuation level
          fin_var[j].reflex_level[1] = recv_data_buff[byte_offset + 3];

        }
        break;

      }

    // Light requests
    case 4: {

        uint8_t  device_offset = 2;

        // (14 bytes each)
        // >>>>> byte 2 to byte 15: LIGHT 0
        // >>>>> byte 16 to byte 29: LIGHT 1
        // >>>>> byte 30 to byte 43: LIGHT 2
        for (uint8_t j = 0; j < NUM_LIGHT; j++) {

          const uint8_t byte_offset = 14 * (j) + device_offset;

          // --- internal variables ----
          // byte x0 --- Ambient light sensor threshold
          temp_val = 0;
          for (uint8_t i = 0; i < wave_size; i++)
            temp_val += recv_data_buff[byte_offset + i + 0] << (8 * i);
          light_var[j].als_threshold = temp_val;

          // byte x2 --- high-power LED cycle period
          temp_val = 0;
          for (uint8_t i = 0; i < wave_size; i++)
            temp_val += recv_data_buff[byte_offset + i + 2] << (8 * i);
          light_var[j].cycle_period = temp_val;

          //--- actuator output variables---
          // byte x4 --- high-power LED level
          light_var[j].led_level = recv_data_buff[byte_offset + 4];

          // byte x5 --- high-power led wave type
          light_var[j].led_wave_type = recv_data_buff[byte_offset + 5];

        }
        break;

      }

    // Type 1 composite request protocol
    case 5: {

        uint8_t  device_offset = 2;
        // (8 bytes each)
        // >>>>> byte 2 to byte 9 : FIN 0
        // >>>>> byte 10 to byte 17 : FIN 1
        // >>>>> byte 18 to byte 25 : FIN 2
        for (uint8_t j = 0; j < NUM_FIN; j++) {

          const uint8_t byte_offset = 8 * (j) + device_offset;

          //--- actuator output variables---

          // byte x0 --- fin motion activation
          fin_var[j].motion_on = recv_data_buff[byte_offset];
          // byte x1 --- reflex actuation level
          fin_var[j].reflex_level[0] = recv_data_buff[byte_offset + 1];
          // byte x2 --- reflex actuation level
          fin_var[j].reflex_level[1] = recv_data_buff[byte_offset + 2];

          // byte x3 --- fin SMA wire 0
          fin_var[j].sma_level[0] = recv_data_buff[byte_offset + 3];
          // byte x4 --- fin SMA wire 1
          fin_var[j].sma_level[1] = recv_data_buff[byte_offset + 4];


        }
        device_offset = 8 * (NUM_FIN) + device_offset;

        // (4 bytes each)
        // >>>>> byte 26 to byte 29: LIGHT 0
        // >>>>> byte 30 to byte 33: LIGHT 1
        // >>>>> byte 34 to byte 37: LIGHT 2
        for (uint8_t j = 0; j < NUM_LIGHT; j++) {

          const uint8_t byte_offset = 4 * (j) + device_offset ;

          //--- actuator output variables---
          // byte x0 --- high-power LED level
          light_var[j].led_level = recv_data_buff[byte_offset];

        }
        break;


      }

    // wave forms
    case 10: {

        //byte 2 wave type to change
        uint8_t wave_type = recv_data_buff[2];

        if (wave_type < NUM_WAVE) {

          // byte 12 to 43 --- indicator LED wave
          for (uint8_t i = 0; i < wave_size; i++)
            wave[wave_type].waveform[i] = recv_data_buff[i + 12];
        }
        break;
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

void CBLATestBed::compose_reply(byte front_signature, byte back_signature, byte msg_setting) {


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

        for (uint8_t j = 0; j < NUM_FIN; j++) {

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

        device_offset = 14 * NUM_FIN + device_offset;

        // (4 bytes each)
        // >>>>> byte 2 to byte 5: Light 0
        // >>>>> byte 6 to byte 9: Light 0
        // >>>>> byte 10 to byte 13: Light 0

        for (uint8_t j = 0; j < NUM_LIGHT; j++) {

          const uint8_t byte_offset = 4 * (j) + device_offset;

          // byte x0 --- ambient light sensor 0 state
          for (uint8_t i = 0; i < 2; i++)
            send_data_buff[byte_offset + i] = light_var[j].als_state >> (8 * i);
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
void CBLATestBed::sample_inputs() {

  sample_inputs(0);
}

void CBLATestBed::sample_inputs(const uint8_t setting) {


  //>>>Fin<<<

  for (uint8_t j = 0; j < NUM_FIN; j++) {

    //~~IR sensors state~~
    for (uint8_t i = 0; i < 2; i++) {

      noInterrupts();
      fin_var[j].ir_state[i] = fin[j].read_analog_state(i);
      interrupts();

    }
    ;
    //~~Accelerometer~~
    noInterrupts();
    fin[j].read_acc_state(fin_var[j].acc_state[0],
                          fin_var[j].acc_state[1],
                          fin_var[j].acc_state[2]);

    interrupts();


  }

  // if (Wire.frozen){
  // //digitalWrite(PGM_DO_pin, 1);
  // digitalWrite(13, 1);
  // }



  //>>>LIGHT<<<

  for (uint8_t j = 0; j < NUM_LIGHT; j++) {

    //~~Ambient Light Sensor~~
    noInterrupts();
    light_var[j].als_state = light[j].read_analog_state();;
    interrupts();
  }


}



//===========================================================================
//============ BEHAVIOUR CODES =========
//===========================================================================

//---- inactive behaviour ----
void CBLATestBed::inactive_behaviour() {

  //=== Fin ===
  for (uint8_t i = 0; i < NUM_FIN; i++) {

    fin[i].set_led_level(0, 0);
    fin[i].set_led_level(1, 0);

    fin[i].set_sma_level(0, 0);
    fin[i].set_sma_level(1, 0);

  }


  //=== testing Light
  for (uint8_t i = 0; i < NUM_FIN; i++) {

    light[i].set_led_level(0);

  }

}

//---- test behaviour ----
void CBLATestBed::test_behaviour(const uint32_t &curr_time) {

  //=== testing Fin ===
  for (uint8_t i = 0; i < NUM_FIN; i++) {
    uint16_t ir_range = fin[i].read_analog_state(0);
    if (ir_range > 1200) {
      fin[i].set_led_level(0, 250);
      fin[i].set_led_level(1, 250);
    }
    else {
      fin[i].set_led_level(0, 0);
      fin[i].set_led_level(1, 0);
    }

    ir_range = fin[i].read_analog_state(1);

    if (ir_range < 00) {
      fin[i].set_sma_level(0, 250);
      fin[i].set_sma_level(1, 250);

    }
    else {
      fin[i].set_sma_level(0, 0);
      fin[i].set_sma_level(1, 0);
    }
  }


  //=== testing Light
  for (uint8_t i = 0; i < NUM_LIGHT; i++) {
    uint16_t ir_range = fin[i].read_analog_state(0);
    if (ir_range > 1200) {
      light[i].set_led_level(20);
    }
    else {
      light[i].set_led_level(0);
    }

  }

}

void CBLATestBed::fin_arm_test_behaviour(const uint32_t &curr_time) {

  //---- Fin cycling variables -----
  static uint32_t high_level_ctrl_fin_phase_time[NUM_FIN] = {0, 0, 0};


  static uint8_t high_level_ctrl_sma0[NUM_FIN] = {0, 0, 0};
  static uint8_t high_level_ctrl_sma1[NUM_FIN] = {1, 1, 1};



  //~~~ fin cycle~~~~
  for (uint8_t j = 0; j < NUM_FIN; j++) {



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
      fin[j].set_sma_level(high_level_ctrl_sma0[j], 255);
      fin[j].set_sma_level(high_level_ctrl_sma1[j], 255);
    }
    else {


      volatile uint32_t cycle_time = curr_time - high_level_ctrl_fin_phase_time[j];

      // if reaches the full period, restart cycle
      if (cycle_time > (uint32_t)(((fin_var[j].arm_cycle_period[1] + fin_var[j].arm_cycle_period[0]) * 100))) {
        fin_var[j].cycling  = 0;
        fin_var[j].motion_on = 0;
      }

      //if reaches the on period
      else if (cycle_time > (uint32_t)(fin_var[j].arm_cycle_period[0] * 100)) {
        fin[j].set_sma_level(high_level_ctrl_sma1[j], 0);
        fin[j].set_sma_level(high_level_ctrl_sma0[j], 0);

      }

    }


  }


}


//---- indicator LED -----

void CBLATestBed::led_blink_behaviour(const uint32_t &curr_time) {

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

void CBLATestBed::led_wave_behaviour(const uint32_t &curr_time) {


  //static WaveTable test_wave(5);
  wave[0].set_duration(10000);
  uint8_t led_level = wave[0].wave_function(curr_time);
  //light.set_led_level(led_level);
  analogWrite(5, led_level);


}

void CBLATestBed::reflex_test_behaviour() {

  //=== testing Fin ===
  for (uint8_t i = 0; i < NUM_FIN; i++) {
    uint16_t ir_range = fin_var[i].ir_state[0];
    if (ir_range > 1200) {
      fin[i].set_led_level(0, 150);
      fin[i].set_led_level(1, 150);
    }
    else {
      fin[i].set_led_level(0, 0);
      fin[i].set_led_level(1, 0);
    }
  }
}

//----- LOW-LEVEL CONTROL -------
void CBLATestBed::low_level_control_fin_behaviour() {


  //>>>> FIN <<<<<
  for (uint8_t j = 0; j < NUM_FIN; j++) {

    fin[j].set_sma_level(0, fin_var[j].sma_level[0]);
    fin[j].set_sma_level(1, fin_var[j].sma_level[1]);
    fin[j].set_led_level(0, fin_var[j].reflex_level[0]);
    fin[j].set_led_level(1, fin_var[j].reflex_level[1]);
  }
}
void CBLATestBed::low_level_control_fin_reflex_behaviour() {


  //>>>> FIN <<<<<
  for (uint8_t j = 0; j < NUM_FIN; j++) {

    fin[j].set_led_level(0, fin_var[j].reflex_level[0]);
    fin[j].set_led_level(1, fin_var[j].reflex_level[1]);
  }
}

void CBLATestBed::low_level_control_light_behaviour() {
  //>>>> LIGHT <<<<<
  for (uint8_t j = 0; j < NUM_LIGHT; j++) {

    light[j].set_led_level(light_var[j].led_level);
  }



}

//----- HIGH-LEVEL CONTROL -------
void CBLATestBed::high_level_control_fin_reflex_behaviour(const uint32_t &curr_time) {


  //---- Fin cycling variables -----
  //static uint16_t high_level_ctrl_fin_reflex_period[NUM_FIN] = {1000, 1000, 1000};

  for (uint8_t j = 0; j < NUM_FIN; j++) {


    bool reflex_on = false;

    //if something is very close
    if (fin_var[j].ir_state[0] > fin_var[j].ir_threshold[0]) {
      reflex_on = true;
      //high_level_ctrl_fin_reflex_period[j] = fin_var[j].reflex_period[0];
    }
    //if there is no object detected
    else {
      reflex_on = false;
    }

    for (uint8_t i = 0; i < NUM_LIGHT; i++) {

      //Actuation

      if (reflex_on) {
        fin[j].set_led_level(i, 128);
        // wave[fin_var[j].fin_reflex_wave_type[i]].set_duration(fin_var[j].fin_reflex_period[i]);
        // uint8_t reflex_level = wave[fin_var[j].fin_reflex_wave_type[i]].wave_function(curr_time);
        // fin[j].set_led_level(i, reflex_level);
      }
      else {
        fin[j].set_led_level(i, 0);

        // uint8_t reflex_level = 0;

        // fin[j].set_led_level(i, reflex_level);
        // wave[fin_var[j].fin_reflex_wave_type[i]].restart_wave_function();
      }
    }

  }



}

void CBLATestBed::high_level_direct_control_fin_arm_behaviour(const uint32_t &curr_time) {

  //---- Fin cycling variables -----
  static uint32_t high_level_ctrl_fin_phase_time[NUM_FIN] = {0, 0, 0};


  static uint8_t high_level_ctrl_sma0[NUM_FIN] = {0, 0, 0};
  static uint8_t high_level_ctrl_sma1[NUM_FIN] = {1, 1, 1};



  //~~~ fin cycle~~~~
  for (uint8_t j = 0; j < NUM_FIN; j++) {

    if (fin_var[j].motion_on < 1 && fin_var[j].cycling < 1) {

      fin[j].set_sma_level(0, 0);
      fin[j].set_sma_level(1, 0);
      fin_var[j].cycling  = 0;
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
      fin_var[j].cycling = 1; //fin_var[j].fin_motion_on;
      high_level_ctrl_fin_phase_time[j] = millis();

      // turn on the first sma
      fin[j].set_sma_level(high_level_ctrl_sma0[j], 255);
      fin[j].set_sma_level(high_level_ctrl_sma1[j], 255);
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


}

void CBLATestBed::high_level_direct_control_fin_arm_behaviour_continuous(const uint32_t &curr_time) {

  //---- Fin cycling variables -----
  static uint32_t high_level_ctrl_fin_phase_time[NUM_FIN] = {0, 0, 0};


  static uint8_t high_level_ctrl_sma0[NUM_FIN] = {0, 0, 0};
  static uint8_t high_level_ctrl_sma1[NUM_FIN] = {1, 1, 1};



  //~~~ fin cycle~~~~
  for (uint8_t j = 0; j < NUM_FIN; j++) {

    if (fin_var[j].motion_on < 1) {

      fin[j].set_sma_level(0, 0);
      fin[j].set_sma_level(1, 0);
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
      fin[j].set_sma_level(high_level_ctrl_sma0[j], 255);
      fin[j].set_sma_level(high_level_ctrl_sma1[j], 255);
    }
    else {


      volatile uint32_t cycle_time = curr_time - high_level_ctrl_fin_phase_time[j];

      // if reaches the full period, restart cycle
      if (cycle_time > ((fin_var[j].arm_cycle_period[1] + fin_var[j].arm_cycle_period[0]) * 100)) {
        fin_var[j].cycling  = 0;
      }

      //if reaches the on period
      else if (cycle_time > (fin_var[j].arm_cycle_period[0] * 100)) {
        fin[j].set_sma_level(high_level_ctrl_sma1[j], 0);
        fin[j].set_sma_level(high_level_ctrl_sma0[j], 0);

      }

    }


  }


}
