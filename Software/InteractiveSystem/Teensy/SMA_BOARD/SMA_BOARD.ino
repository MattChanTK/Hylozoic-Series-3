#define ACCEL 0x53 //Accel I2C Address    

#define ACC_ACT_ADDR 0x27 //ACC Activity/Inactivity control byte
#define ACC_ACT_VAL  0x00 

#define ACC_BW_ADDR 0x2C //ACC BW control byte
#define ACC_BW_VAL  0x0D 

#define ACC_PWRCTRL_ADDR 0x2D //ACC Power control byte
#define ACC_PWRCTRL_SLEEP  0x00 
#define ACC_PWRCTRL_MEASURE  0x08 

#define ACC_INRPPT_ADDR 0x2E //ACC Interupt control byte
#define ACC_INRPPT_DISABLE  0x00  //disable interupt

#define ACC_DATAFORMAT_ADDR 0x31 //ACC data format byte
#define ACC_DATAFORMAT_VALUE  0x00  //Set the range to +/- 16g and make the value right justified with sign extention

#define ACC_FIFO_ADDR 0x38 //ACC FIFO byte
#define ACC_FIFO_VALUE  0x00  // Bypass FIFO

#define ACC_X_LSB_ADDR  0x34// ACC X axis LSB byte
 
#define I2C_MULT_ADDR_0 2
#define I2C_MULT_ADDR_1 24
#define I2C_MULT_ADDR_2 33


#include <i2c_t3.h>

byte accel_jack_map[6];


int i ;

short accel_x;
short accel_y;
short accel_z;


byte buffer[6];   // Array to store ADC values 

void setup() {
pinMode(13, OUTPUT);
  Serial.begin(9600);
  
  accel_jack_map [0] = 4;
  accel_jack_map [1] = 6;
  accel_jack_map [2] = 7;
  accel_jack_map [3] = 2;
  accel_jack_map [4] = 1;
  accel_jack_map [5] = 0;
  
  
  Wire.begin(I2C_MASTER,0x00, I2C_PINS_18_19, I2C_PULLUP_EXT, I2C_RATE_400);
  


  pinMode(I2C_MULT_ADDR_0,OUTPUT);
  pinMode(I2C_MULT_ADDR_1,OUTPUT);
  pinMode(I2C_MULT_ADDR_2,OUTPUT);
  
  
  //Reading Accel
  switchToAccel(2);

  
  delay(1);
 
  writeTo(ACCEL, ACC_ACT_ADDR, ACC_ACT_VAL);  
  writeTo(ACCEL, ACC_BW_ADDR, ACC_BW_VAL);
  writeTo(ACCEL, ACC_PWRCTRL_ADDR, ACC_PWRCTRL_SLEEP);
  writeTo(ACCEL, ACC_PWRCTRL_ADDR, ACC_PWRCTRL_MEASURE);
  writeTo(ACCEL, ACC_INRPPT_ADDR, ACC_INRPPT_DISABLE);
  writeTo(ACCEL, ACC_DATAFORMAT_ADDR, ACC_DATAFORMAT_VALUE);
  writeTo(ACCEL, ACC_FIFO_ADDR, ACC_FIFO_VALUE);

  delay(100);

       digitalWrite(13, 1);
}


void loop() {
  
  

  int i = 0;
  Wire.beginTransmission(ACCEL);
  Wire.write(ACC_X_LSB_ADDR);
  Wire.endTransmission(I2C_NOSTOP, 100);
  
  Wire.requestFrom(ACCEL,2); // Read 4 bytes      
  
  while(Wire.available())
  {
   buffer[i] = Wire.read();
   i++;
  }

  accel_x = buffer[1] << 8 | buffer[0];



}

// switching to the proper accel
void switchToAccel(int aceel_jack_num) {
  
  digitalWrite (I2C_MULT_ADDR_0,(accel_jack_map[aceel_jack_num-1] & 1) > 0);
  digitalWrite (I2C_MULT_ADDR_1,(accel_jack_map[aceel_jack_num-1] & 2) > 0);
  digitalWrite (I2C_MULT_ADDR_2,(accel_jack_map[aceel_jack_num-1] & 4) > 0);
}

// Write a value to address register on device
void writeTo(int device, byte address, byte val) {
  Wire.beginTransmission(device); // start transmission to device 
  Wire.write(address);            // send register address
  Wire.write(val);                // send value to write
  Wire.endTransmission(I2C_NOSTOP, 100);         // end transmission
}
