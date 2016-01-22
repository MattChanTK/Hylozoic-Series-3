#include <i2c_t3.h>

// Command definitions
#define WRITE    0x10
#define READ     0x20
#define SETRATE  0x30

// Function prototypes
void print_i2c_setup(void);
void print_i2c_status(void);
void print_rate(i2c_rate rate);
void test_rate(uint8_t target, i2c_rate rate);

// Memory
#define MEM_LEN 256
uint8_t databuf[MEM_LEN];

bool blinkHigh = false;
elapsedMillis blinkTimer;
elapsedMillis SerialTimer;
elapsedMillis heartbeatTime;

int resetCount = 0;

void setup()
{
    pinMode(LED_BUILTIN,OUTPUT);    // LED
    digitalWrite(LED_BUILTIN,LOW);  // LED off
    pinMode(12,INPUT_PULLUP);       // Control for Test1
    pinMode(11,INPUT_PULLUP);       // Control for Test2
    pinMode(10,INPUT_PULLUP);       // Control for Test3
    pinMode(9,INPUT_PULLUP);        // Control for Test4
    pinMode(8,INPUT_PULLUP);        // Control for Test5

    digitalWrite(LED_BUILTIN, HIGH);
    Serial.begin(9600);
    delay(2000);

    Serial.println("Turned On!");
    digitalWrite(LED_BUILTIN, LOW);
    delay(100);

    // Setup for Master mode, pins 18/19, internal pullups, 400kHz
    Wire.begin(I2C_MASTER, 0x00, I2C_PINS_18_19, I2C_PULLUP_INT, I2C_RATE_100);

    Serial.println("Wire Connected.");
}

void loop()
{
    size_t addr, len;
    uint8_t databuf[256];
    uint8_t target = 0x44; // slave addr
    uint32_t count;

    for( byte i = 0; i <= 5; i++ ){
      Wire.beginTransmission(target);
      Wire.write(i);                  // WRITE command
      Wire.endTransmission();             // blocking write (when not specified I2C_STOP is implicit)

      Serial.println(i);
      
      elapsedMillis delayTimer;
      while( delayTimer < 1000 ){
        if( blinkTimer > 500 ){
          blinkHigh = !blinkHigh;
          digitalWrite(LED_BUILTIN, blinkHigh);
          blinkTimer = 0;
        }
      }
    }

    if( heartbeatTime > 100 ){
      Serial.print("Reset Count: ");
      Serial.print(resetCount);
      Serial.print(" | ");
      print_i2c_status();
      heartbeatTime = 0;
    }

    int sda_pin = 18;
    int scl_pin = 19;
    switch(Wire.status())
    {
      case I2C_ADDR_NAK:
        resetCount++;
        Wire.resetBus();

      default: break;
    }
  
}

//
// print current setup
//
void print_i2c_setup()
{
    Serial.print("Mode:");
    switch(Wire.i2c->opMode)
    {
    case I2C_OP_MODE_IMM: Serial.print("IMM    "); break;
    case I2C_OP_MODE_ISR: Serial.print("ISR    "); break;
    case I2C_OP_MODE_DMA: Serial.printf("DMA[%d] ",Wire.i2c->DMA->channel); break;
    }
    Serial.print("Pins:");
    switch(Wire.i2c->currentPins)
    {
    case I2C_PINS_18_19: Serial.print("18/19 "); break;
    case I2C_PINS_16_17: Serial.print("16/17 "); break;
    case I2C_PINS_22_23: Serial.print("22/23 "); break;
    case I2C_PINS_29_30: Serial.print("29/30 "); break;
    case I2C_PINS_26_31: Serial.print("26/31 "); break;
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


//
// print I2C rate
//
void print_rate(i2c_rate rate)
{
    switch(rate)
    {
    case I2C_RATE_100: Serial.print("I2C_RATE_100"); break;
    case I2C_RATE_200: Serial.print("I2C_RATE_200"); break;
    case I2C_RATE_300: Serial.print("I2C_RATE_300"); break;
    case I2C_RATE_400: Serial.print("I2C_RATE_400"); break;
    case I2C_RATE_600: Serial.print("I2C_RATE_600"); break;
    case I2C_RATE_800: Serial.print("I2C_RATE_800"); break;
    case I2C_RATE_1000: Serial.print("I2C_RATE_1000"); break;
    case I2C_RATE_1200: Serial.print("I2C_RATE_1200"); break;
    case I2C_RATE_1500: Serial.print("I2C_RATE_1500"); break;
    case I2C_RATE_1800: Serial.print("I2C_RATE_1800"); break;
    case I2C_RATE_2000: Serial.print("I2C_RATE_2000"); break;
    case I2C_RATE_2400: Serial.print("I2C_RATE_2400"); break;
    case I2C_RATE_2800: Serial.print("I2C_RATE_2800"); break;
    case I2C_RATE_3000: Serial.print("I2C_RATE_3000"); break;
    }
}


//
// test rate
//
void test_rate(uint8_t target, i2c_rate rate)
{
    uint8_t fail;
    size_t len;

    for(len = 0; len < 256; len++)  // prepare data to send
        databuf[len] = len;         // set data (equal to addr)

    // Change Slave rate
    Wire.beginTransmission(target); // slave addr
    Wire.write(SETRATE);            // SETRATE command
    Wire.write((uint8_t)rate);      // rate
    Wire.endTransmission();         // blocking write

    // Change Master rate
    Wire.setRate(rate);

    // Setup write buffer
    Wire.beginTransmission(target); // slave addr
    Wire.write(WRITE);              // WRITE command
    Wire.write(0);                  // memory address
    for(len = 0; len < 256; len++)  // write block
        Wire.write(databuf[len]);

    // Write to Slave
    elapsedMicros deltaT;
    Wire.endTransmission();         // blocking write
    uint32_t deltatime = deltaT;
    fail = Wire.getError();

    if(!fail)
    {
        Wire.beginTransmission(target);     // slave addr
        Wire.write(READ);                   // READ command
        Wire.write(0);                      // memory address
        Wire.endTransmission(I2C_NOSTOP);   // blocking write (NOSTOP triggers RepSTART on next I2C command)
        Wire.requestFrom(target,256,I2C_STOP);// blocking read
        fail = Wire.getError();

        if(!fail)
        {
            for(len = 0; len < 256; len++)  // verify block
                if(databuf[len] != Wire.readByte()) { fail=1; break; }
        }
    }
    print_i2c_setup();
    if(!fail)
    {
        // Print result
        Serial.print("256 byte transfer at ");
        print_rate(rate);
        Serial.print(" (Actual Rate:");
        print_rate(Wire.i2c->currentRate);
        Serial.print(")");
        Serial.printf(" : %d us : ",deltatime);
        print_i2c_status();
    }
    else
    {
        Serial.printf("Transfer fail : %d us : ",deltatime);
        print_i2c_status();
    }
}
