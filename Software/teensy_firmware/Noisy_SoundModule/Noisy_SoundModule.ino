/*
 * A simple hardware test which receives audio from the audio shield
 * Line-In pins and send it to the Line-Out pins and headphone jack.
 *
 * This example code is in the public domain.
 */

#include <Audio.h>
#include <Wire.h>
#include <SPI.h>
#include <SD.h>

AudioSynthNoiseWhite     noise1;         //xy=83.88888549804688,311.8888854980469
AudioFilterStateVariable bandpassFilter;        //xy=233.88888549804688,308.8888854980469
AudioEffectEnvelope      envelope1;      //xy=418.8888854980469,417.8888854980469



AudioInputI2S          audioInput;         // audio shield: mic or line-in
AudioSynthWaveformSine sinewave;
AudioAnalyzeFFT1024    myFFT;
AudioOutputI2S         audioOutput;        // audio shield: headphones & line-out
AudioAnalyzePeak     	peak_L;
AudioAnalyzePeak     	peak_R;


AudioConnection         patchCord1(noise1, 0, bandpassFilter, 0);
AudioConnection         patchCord2(bandpassFilter, 1, envelope1, 0);
AudioConnection 		patchCord3(envelope1, 0, audioOutput, 0);
AudioConnection 		patchCord4(audioInput, 0, myFFT, 0);
AudioConnection 		patchCord5(audioInput, 0, peak_L, 0);
AudioConnection 		patchCord6(audioInput, 1, peak_R, 0);


AudioControlSGTL5000     sgtl5000_1;     //xy=302,184


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


const int myInput = AUDIO_INPUT_LINEIN;
const int numWindows = 30;
int freqWindows[numWindows];
int senseWindows[numWindows];
int ampWindows[numWindows];
int curWindow = 0;
int curAmpWindow = 0;
int clock_rate = 2000;

void setup() {
  // Audio connections require memory to work.  For more
  // detailed information, see the MemoryAndCpuUsage example
  AudioMemory(100);

  // Enable the audio shield, select input, and enable output
  sgtl5000_1.enable();
  sgtl5000_1.inputSelect(myInput);
  sgtl5000_1.volume(0.5);
  
  //enable the noise1
  noise1.amplitude(0.2);
  
  //adjust filter1 frequency
  bandpassFilter.frequency(3000);
  bandpassFilter.resonance(50);
  
  //adjust the envelope1
  envelope1.delay(0);
  envelope1.attack(20);
  envelope1.hold(20);
  envelope1.decay(20);
  envelope1.sustain(0);
  
  // Configure the window algorithm to use
  myFFT.windowFunction(AudioWindowHanning1024);
  
  // Create a synthetic sine wave, for testing
  // To use this, edit the connections above
  sinewave.amplitude(0.8);
  sinewave.frequency(20);
  
  for (int win=0; win < numWindows; win++){
	freqWindows[win] = 0;
	}

  
}

long int prev_time = millis();
long int prev_time_smooth = millis();

int target_clk_rate = 1500;
int curr_clk_rate = 1500;

void loop() {
	
	float n;
	int i;
	if (peak_L.available()) {
	  ampWindows[curAmpWindow] = peak_L.read() * 100;
	  curAmpWindow++;
	  if (curAmpWindow >= numWindows){
			curAmpWindow = 0;
	  }
	}
	
	if (myFFT.available()) {
	
		for (int i=0; i<bins; i++) {
		  valFFT[i] = myFFT.output[i];
		}
		// Calculate SCG
		SCG = calcSCG(valFFT, lowF, highF);
		
		// Calculate max Freq and Magnitude
		maxFreq(valFFT, lowF, highF);

		// Calculate overall average value
		aV = calcAVG(valFFT, lowF, highF);

		freqWindows[curWindow] = mFdata[0];
		senseWindows[curWindow] = mFdata[1];
		curWindow++;
		if (curWindow >= numWindows){
			curWindow = 0;
		}
	}
	
	//find the average
	long int avg_freq = 0;
	for (int win=0; win < numWindows; win++){
		avg_freq += freqWindows[win];
	}
	avg_freq /= numWindows;
	
	long int avg_sense = 0;
	for (int win=0; win < numWindows; win++){
		avg_sense += senseWindows[win];
	}
	avg_sense /= numWindows;
	
	
	
	if (avg_sense >1600){
		bandpassFilter.frequency(avg_freq);
	}

	long int avg_amp = 0;
	for (int win=0; win < numWindows; win++){
		avg_amp += ampWindows[win];
	}
	avg_amp /= numWindows;
	
	if (avg_amp  < 20){

		target_clk_rate = 1500;
	}
	else{
		target_clk_rate = 1500 - avg_amp *15;
		if (target_clk_rate < 10){
			target_clk_rate = 10;
		}
	}

	if (millis() - prev_time > curr_clk_rate){
		envelope1.noteOn();
		prev_time = millis();
			
		
	}
	if (millis() - prev_time_smooth > 1){
		if (curr_clk_rate < target_clk_rate){
			
			curr_clk_rate += 2;
		}
		else{
			curr_clk_rate = target_clk_rate;
		}
		prev_time_smooth = millis();
	}
	Serial.print(avg_freq);
	Serial.print(", ");
	Serial.print(avg_sense);
	Serial.print(", ");
	Serial.print(avg_amp);
	Serial.print(", ");
	Serial.println(curr_clk_rate);
	

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



