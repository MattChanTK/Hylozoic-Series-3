
//==== constants ====
const unsigned int numOutgoingByte = 64;
const unsigned int numIncomingByte = 64;
const unsigned int period = 0;

//==== pin assignments ====
const unsigned short indicator_led_pin = 13;
const unsigned short analog_0_pin = A0;

//==== internal global variables =====
byte outgoingByte[numOutgoingByte];
byte incomingByte[numIncomingByte];
unsigned long msUntilNextSend = millis() + period;
unsigned int packetCount = 0;
volatile boolean ledState = 1;

//----- indicator LED on -----
volatile boolean indicator_led_on = true;
volatile boolean indicator_led_on_0 = false;
//----- indicator LED blink ------
IntervalTimer indicator_led_blinkTimer;
volatile int indicator_led_blinkPeriod_0 = -99;
volatile int indicator_led_blinkPeriod = 0;

//----- analog 0 ------
volatile unsigned int analog_0_state = 0;

void setup() {
  
  //---- indicator led ----
  pinMode(indicator_led_pin, OUTPUT);
  digitalWrite(indicator_led_pin, ledState);  
  indicator_led_blinkTimer.begin(blinkLED, indicator_led_blinkPeriod_0);
  
  //---- analog read -----
  pinMode(analog_0_pin, INPUT);
}


void blinkLED(void){
    ledState ^= 1;
    digitalWrite(indicator_led_pin, ledState);  
}

boolean receive_msg(byte recv_data_buff[], byte send_data_buff[]){
  
    noInterrupts();
    unsigned short byteCount = RawHID.recv(recv_data_buff, 0);
    interrupts();
  
    if (byteCount > 0) {
      
      // sample the sensors
      sample_inputs();
      
      // extract the front and end signaures
      byte front_signature = recv_data_buff[0];
      byte back_signature = recv_data_buff[numIncomingByte-1];
  
      // compose reply message
      compose_reply(send_data_buff, front_signature, back_signature);
      send_msg(send_data_buff);
      return true;
    }
    else{
      return false;
    }
}

void send_msg(byte data_buff[]){
  
  // Send a message
   noInterrupts();
   RawHID.send(data_buff, 10);
   interrupts();
}

void parse_msg(byte data_buff[]){
  
  // byte 2 --- indicator led on or off
  indicator_led_on = data_buff[2];
  
  // byte 3 and 4 --- indicator led blinking frequency
  int val = 0;
  for (int i = 0; i < 2 ; i++)
    val += data_buff[i+3] << (8*i);
  indicator_led_blinkPeriod = val*1000;
}

void sample_inputs(){
  analog_0_state = analogRead(analog_0_pin);
}

void compose_reply(byte data_buff[], byte front_signature, byte back_signature){
  
  // add the signatures to first and last byte
  data_buff[0] = front_signature;
  data_buff[numOutgoingByte-1] = back_signature;
  
  // byte 1 and 2 --- analog 0
  for (int i = 0; i < 2 ; i++)
    data_buff[i+1] = analog_0_state >> (8*i);
  
}


void loop() {
  
  
  // check for new messages
   if (receive_msg(incomingByte, outgoingByte)){
    
     // parse the message and save to parameters
     parse_msg(incomingByte);
   
     //----the behaviour codes----
     
     //..... indicator LED .....
     // if it should be on
     if (indicator_led_on == 1){
       
       
       // if there is a change in blink period
       if (indicator_led_blinkPeriod != indicator_led_blinkPeriod_0 ||
           indicator_led_on != indicator_led_on_0){
         indicator_led_on_0 = indicator_led_on;
         indicator_led_blinkPeriod_0 = indicator_led_blinkPeriod;
         
         //update the blinker's period
         if (indicator_led_blinkPeriod > 0){
           indicator_led_blinkTimer.begin(blinkLED, indicator_led_blinkPeriod);
         }
         //if the period is 0 just end the blink timer and and turn it on 
         else if (indicator_led_blinkPeriod == 0){
           indicator_led_blinkTimer.end();
           ledState = 1;
           digitalWrite(indicator_led_pin, ledState);
         }
       }
     }
     // if it should be off
     else if (indicator_led_on == 0){ 
       indicator_led_on_0 = indicator_led_on;
       // end the blink timer and turn it off
       indicator_led_blinkTimer.end();
       ledState = 0;
       digitalWrite(indicator_led_pin, ledState);
     }
   }
   
   

}


