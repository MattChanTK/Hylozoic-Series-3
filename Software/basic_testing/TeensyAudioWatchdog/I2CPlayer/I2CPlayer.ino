#define __USE_I2C_T3__

#include <Audio.h>
#ifdef __USE_I2C_T3__
  #include <i2c_t3.h>
#else
  #include <Wire.h> // Had to edit control_wm8731.cpp and control_sgtl5000.cpp to use i2c_t3.h instead of Wire.h
#endif
#include <SPI.h>
#include <SD.h>
#include <SerialFlash.h>
#include <Bounce.h>

// WAV files converted to code by wav2sketch
#include "AudioSampleSnare.h"        // http://www.freesound.org/people/KEVOY/sounds/82583/
#include "AudioSampleTomtom.h"       // http://www.freesound.org/people/zgump/sounds/86334/
#include "AudioSampleHihat.h"        // http://www.freesound.org/people/mhc/sounds/102790/
#include "AudioSampleKick.h"         // http://www.freesound.org/people/DWSD/sounds/171104/
#include "AudioSampleGong.h"         // http://www.freesound.org/people/juskiddink/sounds/86773/
#include "AudioSampleCashregister.h" // http://www.freesound.org/people/kiddpark/sounds/201159/

//Watchdog Timer
#include "watchdog.h"

// Create the Audio components.  These should be created in the
// order data flows, inputs/sources -> processing -> outputs
//
AudioPlayMemory    sound0;
AudioPlayMemory    sound1;  // six memory players, so we can play
AudioPlayMemory    sound2;  // all six sounds simultaneously
AudioPlayMemory    sound3;
AudioPlayMemory    sound4;
AudioPlayMemory    sound5;
AudioMixer4        mix1;    // two 4-channel mixers are needed in
AudioMixer4        mix2;    // tandem to combine 6 audio sources
AudioOutputI2S     headphones;
AudioOutputAnalog  dac;     // play to both I2S audio board and on-chip DAC

// Create Audio connections between the components
//
AudioConnection c1(sound0, 0, mix1, 0);
AudioConnection c2(sound1, 0, mix1, 1);
AudioConnection c3(sound2, 0, mix1, 2);
AudioConnection c4(sound3, 0, mix1, 3);
AudioConnection c5(mix1, 0, mix2, 0);   // output of mix1 into 1st input on mix2
AudioConnection c6(sound4, 0, mix2, 1);
AudioConnection c7(sound5, 0, mix2, 2);
AudioConnection c8(mix2, 0, headphones, 0);
AudioConnection c9(mix2, 0, headphones, 1);
AudioConnection c10(mix2, 0, dac, 0);

// Create an object to control the audio shield.
// 
AudioControlSGTL5000 audioShield;

// From the slave sample from the i2c_t3 library

// Command definitions
#define WRITE    0x10
#define READ     0x20
#define SETRATE  0x30

// Function prototypes
#ifdef __USE_I2C_T3__
void receiveEvent(size_t len);
#else
void receiveEvent(int len);
#endif
void requestEvent(void);

// Memory
#define MEM_LEN 256
uint8_t mem[MEM_LEN];
uint8_t cmd;
size_t addr;

bool blinkHigh = false;
elapsedMillis blinkTime, heartbeatTime, sketchTime, watchdogTime;

void setup() {

  // Audio connections require memory to work.  For more
  // detailed information, see the MemoryAndCpuUsage example
  AudioMemory(10);

  // turn on the output
  audioShield.enable();
  audioShield.volume(0.5);
  audioShield.dacVolume(1.0);
  audioShield.adcHighPassFilterEnable();
  // audioShield.audioPreProcessorEnable();
  // audioShield.enhanceBassEnable();
  audioShield.lineOutLevel(29);
  

  // by default the Teensy 3.1 DAC uses 3.3Vp-p output
  // if your 3.3V power has noise, switching to the
  // internal 1.2V reference can give you a clean signal
  //dac.analogReference(INTERNAL);

  // reduce the gain on mixer channels, so more than 1
  // sound can play simultaneously without clipping
  mix1.gain(0, 0.4);
  mix1.gain(1, 0.4);
  mix1.gain(2, 0.4);
  mix1.gain(3, 0.4);
  mix2.gain(1, 0.4);
  mix2.gain(2, 0.4);

// From the slave sample from the i2c_t3 library
    pinMode(LED_BUILTIN,OUTPUT); // LED

    // Setup for Slave mode, address 0x44, pins 29/30, external pullups, 400kHz
    //Wire.begin(I2C_SLAVE, 0x44, I2C_PINS_18_19, I2C_PULLUP_EXT, I2C_RATE_100); //Version for i2c_t3.h
    Wire.begin(0x44);

    // init vars
    cmd = 0;
    addr = 0;
    memset(mem, 0, sizeof(mem));

    // register events
    Wire.onReceive(receiveEvent);
    Wire.onRequest(requestEvent);

    Serial.begin(9600);
    delay(2000);
    Serial.println("Starting");

    watchdogTime = 0;
    watchdog_setup();
}

void loop() {

  if( blinkTime > 50 ){
    blinkHigh = !blinkHigh;
    digitalWrite(LED_BUILTIN, blinkHigh);
    blinkTime = 0;
  }

  if( heartbeatTime > 100 ){
    print_i2c_status();
    Serial.print(watchdogTime);
    Serial.print(" | ");
    Serial.println(sketchTime);
    heartbeatTime = 0;
  }
  
}

//
// handle Rx Event (incoming I2C request/data)
//
#ifdef __USE_I2C_T3__
void receiveEvent(size_t len)
#else
void receiveEvent(int len)
#endif
{
    if(Wire.available())
    {
        // grab command
        cmd = Wire.read();
        Serial.print("Playing: ");
        Serial.println(cmd);
        switch(cmd)
        {
        /*case WRITE:
            addr = Wire.readByte();                // grab addr
            while(Wire.available())
                if(addr < MEM_LEN)                 // drop data beyond mem boundary
                    mem[addr++] = Wire.readByte(); // copy data to mem
                else
                    Wire.readByte();               // drop data if mem full
            break;

        case READ:
            addr = Wire.readByte();                // grab addr
            break;

        case SETRATE:
            rate = (i2c_rate)Wire.readByte();      // grab rate
            Wire.setRate(rate);                    // set rate
            break;*/
          case 0:
            sound0.play(AudioSampleSnare);
            watchdogTime = 0;
            watchdog_loop();
            break;
          case 1:
            sound1.play(AudioSampleTomtom);
            break;
          case 2:
            sound2.play(AudioSampleHihat);
            break;
          case 3:
            sound3.play(AudioSampleKick);
            break;
          case 4:
            // comment this line to work with Teensy 3.0.
            // the Gong sound is very long, too much for 3.0's memory
            sound4.play(AudioSampleGong);
            break;
          case 5:
            sound5.play(AudioSampleCashregister);
            break;
        }
    }
}

//
// handle Tx Event (outgoing I2C data)
//
void requestEvent(void)
{
    switch(cmd)
    {
    case READ:
        Wire.write(&mem[addr], MEM_LEN-addr); // fill Tx buffer (from addr location to end of mem)
        break;
    }
}

//
// print I2C status
//
void print_i2c_status(void)
{
    switch(Wire.status())
    {
    case I2C_WAITING:  Serial.print("I2C waiting, no errors\n"); break;
    case I2C_ADDR_NAK: Serial.print("Slave addr not acknowledged\n"); break;
    case I2C_DATA_NAK: Serial.print("Slave data not acknowledged\n"); break;
    case I2C_ARB_LOST: Serial.print("Bus Error: Arbitration Lost\n"); break;
    case I2C_TIMEOUT:  Serial.print("I2C timeout\n"); break;
    case I2C_BUF_OVF:  Serial.print("I2C buffer overflow\n"); break;
    case I2C_SENDING:  Serial.print("I2C sending\n"); break;
    case I2C_SEND_ADDR: Serial.print("I2C send addr\n"); break;
    case I2C_RECEIVING: Serial.print("I2C receiving\n"); break;
    case I2C_SLAVE_TX: Serial.print("I2C slave TX\n"); break;
    case I2C_SLAVE_RX: Serial.print("I2C slave RX\n"); break;
    default:           Serial.print("I2C busy\n"); break;
    }
}
