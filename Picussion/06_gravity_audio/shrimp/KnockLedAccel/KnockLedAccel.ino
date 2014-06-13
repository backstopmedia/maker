/* Knock Sensor plus LED control plus ADXL345 accelerometer
  
   This sketch reads a piezo element to detect a knocking sound. 
   It reads an analog pin and compares the result to a set threshold. 
   If the result is greater than the threshold, it writes
   "K:" to the serial port, followed by the analog reading.
   
   The sketch responds to a Serial message "on" followed by a newline by 
   turning on its LED, and responds to "off" followed by a newline by
   turning off its LED.

   Additionally it periodically reads an ADXL345 digital 
   accelerometer over I2C, reading X,Y,Z values, then writing 
   "A:" to the serial port out, followed by the three axis readings.
   
   Based on http://www.arduino.cc/en/Tutorial/Knock created 25 Mar 2007 by David Cuartielles <http://www.0j0.org>
   modified 30 Aug 2011 by Tom Igoe
   modified 25 May 2014 by Cefn Hoile
   
   This example code is in the public domain.

 */
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_ADXL345_U.h>

/* Assign a unique ID to this sensor at the same time */
Adafruit_ADXL345_Unified accel = Adafruit_ADXL345_Unified(12345); 

// these constants won't change:
const int ledPin = 13;      // led connected to digital pin 13
const int knockSensor = A0; // the piezo is connected to analog pin 0
const int threshold = 50;  // threshold value to decide when the detected sound is a knock or not

unsigned long lastKnock = 0; //the last time in milliseconds that a knock was detected
const unsigned long ignoreKnock = 50; //how long to ignore knocks after one is detected (debounce)

// these variables will change:
int sensorReading = 0;      // variable to store the value read from the sensor pin
int ledState = LOW;         // variable used to store the last LED status, to toggle the light

void setup() {
   pinMode(ledPin, OUTPUT); // declare the ledPin as as OUTPUT
   Serial.begin(9600);       // use the serial port
   
  /* Initialise the sensor */
  if(!accel.begin())
  {
    /* There was a problem detecting the ADXL345 ... check your connections */
    Serial.println("Ooops, no ADXL345 detected ... Check your wiring!");
    while(1);
  }   

  accel.setRange(ADXL345_RANGE_16_G);

}

void loop() {
   
  /* Display the acceleration (in m/s^2) */
  sensors_event_t event; 
  accel.getEvent(&event);
  Serial.print("A: "); 
  Serial.print(event.acceleration.x); Serial.print(",");
  Serial.print(event.acceleration.y); Serial.print(",");
  Serial.println(event.acceleration.z);
  
  // read the sensor and store it in the variable sensorReading:
  sensorReading = analogRead(knockSensor);
  
  // if the sensor reading is greater than the threshold:
  if ((sensorReading >= threshold) && ((millis() - lastKnock) > ignoreKnock)) {
    lastKnock = millis();
    // send the string "Knock!" back to the computer, followed by newline
    Serial.print("K:");         
    Serial.println(sensorReading);         
  }

  while(Serial.available()){
    String serialString = Serial.readStringUntil('\n');
    
    if(serialString.equals("on")){
      ledState = HIGH;
    }
    else if(serialString.equals("off")){
      ledState = LOW;
    }
    else{
      Serial.print("Unexpected text:");
      Serial.print(serialString);
      Serial.println();
    }
  }

  digitalWrite(ledPin, ledState);
  
}
