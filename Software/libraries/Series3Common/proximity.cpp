#include "proximity.h"

#define N_CONSEQ_READS 100
#define READ_DELAY_MICRO 10
#define BETWEEN_READ_DELAY 50 // In milliseconds

// Constructor
Proximity::Proximity()
  : pin(0), decay(0.0), reading(0), readDelay(0){
    
  }

void Proximity::init(int _pin, float _decay)  {
  pin = _pin;
  decay = _decay;
  
  // Ensure the proper pinMode for the analogRead pin that is being used.
  //pinMode(pin, INPUT);
  limits.clear();
  limits.set_decay(decay);
}

// Register a new reading from the sensor
void Proximity::read(){
  if( readDelay >= BETWEEN_READ_DELAY ){ // Don't read TOO much faster than human perception
    readDelay = 0;
    
    // Average the reading to ignore outliers
    Statistic avg;
    avg.clear();
    for( int i = 0; i < N_CONSEQ_READS; i++ ){
      avg.add(analogRead(pin));
      delayMicroseconds(READ_DELAY_MICRO);
    }
    reading = (int) avg.average();
    limits.add(reading);
  }
}

// Get the value as a fraction of the decaying limits
float Proximity::value(){
  return limits.decay_fraction(reading);
}

// Get a normalized value, ranged between 0 and 255
int Proximity::normalized_value(){
  return limits.decay_fraction_int(reading);
}

int Proximity::raw(){
  return reading;
}


