/*
  Ping))) Sensor

  This sketch reads a PING))) ultrasonic rangefinder and returns the distance
  to the closest object in range. To do this, it sends a pulse to the sensor to
  initiate a reading, then listens for a pulse to return. The length of the
  returning pulse is proportional to the distance of the object from the sensor.

  The circuit:
	- +V connection of the PING))) attached to +5V
	- GND connection of the PING))) attached to ground
	- SIG connection of the PING))) attached to digital pin 7

  created 3 Nov 2008
  by David A. Mellis
  modified 30 Aug 2011
  by Tom Igoe

  This example code is in the public domain.

  http://www.arduino.cc/en/Tutorial/Ping
*/

// this constant won't change. It's the pin number of the sensor's output:
const int pingPin = 7;

void compute_square_setup();
void compute_square_loop();
void motor_setup();
void motor_loop();
void ping_setup();
void ping_loop();

void setup() {
  // initialize serial communication:
  Serial.begin(9600);
}

void loop() {
  int mode = -1;
  if (Serial.available()) {
    mode = Serial.parseInt();
    Serial.flush();
  }
  switch (mode) {
    case 0:
      ping_setup();
      ping_loop();
      break;
    case 1:
      motor_setup();
      motor_loop();
      break;
    case 2:
      ir_setup();
      ir_loop();
    case 10:
      compute_square_setup();
      compute_square_loop();
      break;
    default:
      //Serial.println("Unrecognized mode");
      break;
  }
}
