elapsedMillis dogTimer;

void setup() {
  Serial.begin(9600);
  delay(1000);

  pinMode(LED_BUILTIN, OUTPUT);

  Serial.println("Starting Up");

  for(int i=0; i<3; i++){
    digitalWrite(LED_BUILTIN, HIGH);
    delay(500);
    digitalWrite(LED_BUILTIN, LOW);
    delay(500);
  }

  dogTimer=0;
  
  WDOG_UNLOCK = WDOG_UNLOCK_SEQ1;
  WDOG_UNLOCK = WDOG_UNLOCK_SEQ2;
  delayMicroseconds(1); // Need to wait a bit..
  WDOG_STCTRLH = 0x0001; // Enable WDG
  WDOG_TOVALL = 2000; // The next 2 lines sets the time-out value. This is the value that the watchdog timer compare itself to in milliseconds
  WDOG_TOVALH = 0;
  WDOG_PRESC = 0; // This sets prescale clock so that the watchdog timer ticks at 1kHZ instead of the default 1kHZ/4 = 200 HZ
}

void loop() {
  for(int j=0; j<5; j++){
    for(int i=0; i<10; i++){
      Serial.print("Looping: ");
      Serial.print(j);
      Serial.print(" | ");
      Serial.print(i);
      Serial.print(" | ");
      Serial.println(dogTimer);
      digitalWrite(LED_BUILTIN, HIGH);
      delay(10);
      digitalWrite(LED_BUILTIN, LOW);
      delay(10);
    }
    Serial.print("Looping: ");
    Serial.println(dogTimer);
    noInterrupts();
    WDOG_REFRESH = 0xA602;
    WDOG_REFRESH = 0xB480;
    interrupts();
    Serial.print("Looping: ");
    Serial.println(dogTimer);
  }
  delay(2000);
  
}
