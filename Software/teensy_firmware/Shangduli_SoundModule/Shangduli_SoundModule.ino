// *** Listening for a specific sound while running Vinegar Battery to sound module SOUND MODULE ***
// Vinegar battery controls delay between triggering of sounds
// Code to perform basic control of the sound module including:
// - 3 analog inputs
//    - A1p = IR
//    - A2p = IR
//    - A3p = Vinegar Battery
// - 2 digital trigger inputs
// - 2 audio channel outputs
// - 2 audio channel inputs
// - 2 low power PWM reflex channels

//*** Variable Initialization ***
// Load required libraries for Teensy Audio Board, I2C communication, and SD Card Reading
#include <Audio.h>
#include <Wire.h>
#include <SPI.h>
#include <SD.h>

// Establish Input and Output Pin variables for Teensy
// Analog Inputs
const int A1p = A6;
const int A2p = A7;
const int A3p = A14;

// PWM ouput pins for reflex channels
const int R1 = 3;
const int R2 = 4;

// Digital Trigger Input Pins
const int DT1 = 1;
const int DT2 = 2;

// Signal output pin 
const int SOUT1 = 5;

// Establsh Variables used in signal processing
const int bins = 512; // Number of bins in FFT
float fs = 44117.647; //Sampling rate
float dF = fs/bins/2.0; // width of FFT bin in Hz
float sf = 3.0; // Scaling Factor of FFT values in DB calculation
float lowF = 200; // Low frequency cutoff for stats calculations
float highF = 6000; // High Frequency cutoff for FFT

float SCG; // Spectral Center of Gravity
float aV;
int mFdata[2];
float cf[bins];
float valFFT[bins];
float dBvalFFT[bins];

boolean printSerial = true;

elapsedMillis T1; // timer object
elapsedMillis T2; // timer object

// Vinegar Battery Variables
int VBdelay = 10000; // Length of time in ms for VB to delay
uint32_t VBmax = 100000; // Maximum delay length in ms 

boolean UNBLOCKAUDIO = HIGH; // BLOCK AUDIO PLAYBACK
int blockT = 2000; // Time to block audio for in milliseconds

//Define 8 Independent Wavfiles for playback in two 4-channel mixers
AudioPlaySdWav           playWav1;       // mixer1 - Left Channel
AudioPlaySdWav           playWav2;       
AudioPlaySdWav           playWav3;       
AudioPlaySdWav           playWav4;       

AudioPlaySdWav           playWav5;       // mixer2 - Right Channel
AudioPlaySdWav           playWav6;       
AudioPlaySdWav           playWav7;       
AudioPlaySdWav           playWav8;       

AudioInputI2S            i2s1;           // set up audio input variable from LINE-IN
AudioAnalyzeFFT1024      fft1024_1;      // FFT input - Left Channel
  //AudioAnalyzeFFT1024      fft1024_2;      // // FFT input - Right Channel - LIBRARY CURRENTLY DOESN'T support this (so leave it commented out)

AudioMixer4              mixer1;         // mixer1 - Left Channel
AudioMixer4              mixer2;         // mixer1 - Right Channel
AudioOutputI2S           i2s2;           // set up audio output through LINE-OUT

AudioConnection          patchCord2(playWav1, 0, mixer1, 0); //Set wav file inputs to mixer1
AudioConnection          patchCord7(playWav2, 0, mixer1, 1);
AudioConnection          patchCord5(playWav3, 0, mixer1, 2);
AudioConnection          patchCord4(playWav4, 0, mixer1, 3);

AudioConnection          patchCord8(playWav5, 0, mixer2, 0); //Set wav file inputs to mixer2
AudioConnection          patchCord6(playWav6, 0, mixer2, 1);
AudioConnection          patchCord3(playWav7, 0, mixer2, 2);
AudioConnection          patchCord1(playWav8, 0, mixer2, 3);

AudioConnection          patchCord9(i2s1, 0, fft1024_1, 0); // FFT of LINE-IN Left Channel
//AudioConnection          patchCord10(i2s1, 1, fft1024_2, 0); // FFT of LINE-IN Left Channel - leave commented

AudioConnection          patchCord11(mixer1, 0, i2s2, 0); // Output mixer1 to LINE-OUT left channel
AudioConnection          patchCord12(mixer2, 0, i2s2, 1); // Output mixer2 to LINE-OUT right channel

AudioControlSGTL5000 sgtl5000_1; //Initialize LINE-OUT control element


//*** SETUP LOOP ***
void setup() {
  Serial.begin(9600);

  // Audio connections require memory to work.  For more
  // detailed information, see the MemoryAndCpuUsage example

  AudioMemory(20); // Establish Audio Memory

  sgtl5000_1.enable(); // Enable LINE-OUT
  sgtl5000_1.volume(1.0); //Set Iniitial LINE-OUT Gain
  fft1024_1.windowFunction(AudioWindowHanning1024); // Define the window applied to FFT
	
  // set up the trigger pins
  pinMode(DT1, INPUT_PULLUP);
  pinMode(DT2, INPUT_PULLUP);
  
  // set up the signal output pins
  pinMode(SOUT1, OUTPUT);
  digitalWrite(SOUT1, LOW);

  SPI.setMOSI(7); //Sets pin for TAB - Don't change
  SPI.setSCK(14); //Sets pin for TAB - Don't change

  // Check SD card is present and readable
  if (!(SD.begin(10))) {
    // stop here, but print a message repetitively
    while (1) {
      Serial.println("Unable to access the SD card");
      delay(500);
    }
  }
  WDOG_UNLOCK = WDOG_UNLOCK_SEQ1;
  WDOG_UNLOCK = WDOG_UNLOCK_SEQ2;
  delayMicroseconds(1); // Need to wait a bit..
  WDOG_STCTRLH = 0x0001; // Enable WDG
  WDOG_TOVALL = 2000; // The next 2 lines sets the time-out value. This is the value that the watchdog timer compare itself to.
  WDOG_TOVALH = 0;
  WDOG_PRESC = 0; // This sets prescale clock so that the watchdog timer ticks at 1kHZ instead of the default 1kHZ/4 = 200 HZ

}



void loop() 
{
  //feed the dog
  delay(1);
  noInterrupts();
  WDOG_REFRESH = 0xA602;
  WDOG_REFRESH = 0xB480;
  interrupts()
  
  // Set criteria to identify a sound
  boolean PEEPTEST;
  if((mFdata[0]>SCG)&& // if the peak frequency > SCG
    (mFdata[0]<2250)&& // and within 1950-2250 Hz
     (mFdata[0]>1950)&&
     ((4.0*20.0*log10(mFdata[1]))>90)){ //and max above a certain threshold
    PEEPTEST = HIGH;  // then PEEP is true, and respond with a peep
  } else {
    PEEPTEST = LOW;
  }

  if(UNBLOCKAUDIO && PEEPTEST){
    playWav2.play("peepback.wav"); // play peep in response
    delay(100);
    playWav6.play("SB51.wav"); // play another call in response too
    UNBLOCKAUDIO = LOW; // block audio so it doesn't respond to itself
    T2 = 0;
  }
  
  if (T2 >= blockT) {
    UNBLOCKAUDIO = HIGH; // unblock audio after a certain amount of time
  }
  
   analogWrite(R1, readAnalog(A1p)); // Map IR value to Reflex LED Value
   analogWrite(R2, readAnalog(A2p)); // Map IR value to Reflex LED Value

   mixer1.gain(0,2); // Set a constant left channel Value
   mixer1.gain(1,2); // Set a constant left channel Value

   mixer2.gain(0,2); // Set a consstant right channel Value
   mixer2.gain(1,2); // Set a consstant right channel Value
  
  // output high on signal pin based on IR input
  if (analogRead(A1p) > 500){
	  
	  digitalWrite(SOUT1, HIGH);
  }
  else{
	  digitalWrite(SOUT1, LOW);
  }

  // play sounds if either of the trigger pins is high
  bool trig1 = false;
  for (int i=0; i < 10; i++){
	  trig1 |= digitalRead(DT1);
  }
  bool trig2 = false;
  trig2 = digitalRead(DT2);
  for (int i=0; i < 10; i++){
	  trig2 |= digitalRead(DT2);
  }
  // Serial.printf("Trig1=%d, Trig2=%d\n", trig1, trig2);
  if (!trig1 && !trig2){
	  playWav1.play("A.wav");
  }
  else if(!trig1 && trig2){
	  playWav1.play("C.wav");
  }
  else if(trig1 && !trig2){
	  playWav1.play("E.wav");
  }
  else{
	  //Play a sound every ~5 seconds on each channel with some random delay
	  if (T1 >= VBdelay) {
		T1 = T1 - VBdelay+random(0, 50000);
		
		int Rnum = random(0,10);
		if(Rnum>8){
		playWav1.play("A.wav");
		} else if (Rnum>5) {
		playWav1.play("B.wav");
		} else if (Rnum>3) {
		playWav1.play("C.wav");
		} else {
		playWav1.play("D.wav");
		}      
		delay(random(500,1000));
		
		Rnum = random(0,10);
		if(Rnum>6){
		playWav5.play("E.wav");
		} else if (Rnum>3) {
		playWav5.play("F.wav");
		} else {
		playWav5.play("G.wav");
		}
		
		VBdelay = (1-float(readAnalog(A3p))/255)*VBmax;   // Set the delay between triggers as a function of VB Voltage
		if(VBdelay < 2000){VBdelay = 1000;} // Set a minimum delay length
	  }  
  }
  // delay for trigger drivern activation
  if (!trig1 || !trig2){
	delay(random(500,1000));	
  }

  if (fft1024_1.available()) {
    for (int i=0; i<bins; i++) {
      valFFT[i] = fft1024_1.output[i];
    }
    // Calculate SCG
    SCG = calcSCG(valFFT, lowF, highF);
    
    // Calculate max Freq and Magnitude
    maxFreq(valFFT, lowF, highF);

    // Calculate overall average value
    aV = calcAVG(valFFT, lowF, highF);

    if(printSerial){
       //SerialPrintToGui();    
    }
  }

}

void SerialPrintToGui(){
    Serial.println(2);
    // each time new FFT data is available
    // print it all to the Arduino Serial Monitor
    const char delim = '\t';
    const char header = '\n';
    Serial.print(header); // send a header character
    for (int i=0; i<bins; i++) {
      Serial.print(valFFT[i]);
      Serial.print(delim);
    }

    // Send SCG
    Serial.print(int(SCG));
    Serial.print(delim);
    
    // Send max Freq and Magnitude
    Serial.print(mFdata[0]);
    Serial.print(delim);
    
    Serial.print(mFdata[1]);
    Serial.print(delim);

    // Send overall average value
    Serial.print(int(aV));
    Serial.print(delim);
    Serial.println();
    delay(50);
    Serial.println(4);
}

// Calculate Spectral Centroid
// FFT array, min frequency, max frequency
float calcSCG(float yFFT[], float minF, float maxF){
    float nSCG = 0;
    float dSCG = 0;
    for(int n=0; n<bins; n++){
      if(((n*dF+0.5*dF)>=minF)&&((n*dF+0.5*dF)<=maxF)){
        nSCG += (n*dF+0.5*dF)*yFFT[n];        
        dSCG += yFFT[n];        
      } else if ((n*dF+0.5*dF)>maxF) {
        break;
      }      
   }   
  return float(nSCG/dSCG);
}

// Frequency Value and magnitude of maximum component
void maxFreq(float yFFT[], float minF, float maxF){
    int indF = 0;
    int yMAX = 0;
    for(int n=0; n<bins-1; n++){
      if(((n*dF+0.5*dF)>=minF)&&((n*dF+0.5*dF)<=maxF)){
        if(yFFT[n+1]>yMAX){
          indF = n;
          yMAX = yFFT[n+1];
        }
      }      
    }
    int n = indF;
    float Freq = (yFFT[n-1]*((n-1)*dF+0.5*dF)+
          yFFT[n]*(n*dF+0.5*dF)+
          yFFT[n+1]*((n+1)*dF+0.5*dF))/(yFFT[n-1]+yFFT[n]+yFFT[n+1]);  

    mFdata[0] = round(Freq); 
    mFdata[1] = yMAX;

}

// Calculate the average magnitude value in the given frequency band
float calcAVG(float yFFT[], float minF, float maxF){
    float yV = 0;
    float nn = 0;
    for(int n=0; n<bins-1; n++){
      if(((n*dF+0.5*dF)>=minF)&&((n*dF+0.5*dF)<=maxF)){
        yV += float(yFFT[n]);
        nn++;
      } else if ((n*dF+0.5*dF)>maxF) {
        break;
      }      
    }
  return float(yV/nn);
}


// Read the provided pin and return it in the range 0-255
int readAnalog(int AnalogPin){
  int AnalogOut = analogRead(AnalogPin)/4;
  return AnalogOut;
}


