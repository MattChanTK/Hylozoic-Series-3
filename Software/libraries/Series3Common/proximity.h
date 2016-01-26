#ifndef _PROXIMITY_H
#define _PROXIMITY_H

#if defined(ARDUINO) && ARDUINO >= 100
  #include "Arduino.h"
#else
  #include "WProgram.h"
#endif

#include "Statistic.h"

class Proximity{
  public:
    Statistic limits;
    int pin;
    float decay;
    int reading;
    elapsedMillis readDelay;
  
    // Constructor
    Proximity();
    
    void init(int _pin, float _decay = 0.001);

    // Register a new reading from the sensor
    void read();

    // Get the value as a fraction of the decaying limits
    float value();

    // Get a normalized value, ranged between 0 and 255
    int normalized_value();
	
	// cpp:function:: int Proximity::raw()
	int raw();
};

#endif
