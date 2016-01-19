#include "proximity.h"

#if defined(ARDUINO) && ARDUINO >= 100
  #include "Arduino.h"
#else
  #include "WProgram.h"
#endif

// Constructor
Proximity::Proximity()
  : pin (0), decay(0.0), reading (0){
    
  }

void Proximity::init(int _pin, float _decay)  {
  pin = _pin;
  
  // Ensure the proper pinMode for the analogRead pin that is being used.
  //pinMode(pin, INPUT);
  limits.clear();
}

// Register a new reading from the sensor
void Proximity::read(){
  reading = analogRead(pin);
  limits.add(reading);
}

// Get the value as a fraction of the decaying limits
float Proximity::value(){
  return limits.decay_fraction(reading);
}

// Get a normalized value, ranged between 0 and 255
int Proximity::normalized_value(){
  return limits.decay_fraction_int(reading);
}

