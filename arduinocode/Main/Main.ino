#include <string.h>

void compute_square_loop();
void motor_setup();
void set_motor();
void ping_loop();
void ir_setup();

void setup() {
  // initialize serial communication:
  Serial.begin(9600);
  motor_setup();
  ir_setup();
}

void loop() {
  motor_setup();
  int mode = -1;
  if (Serial.available()) {
    char input[1];
    Serial.readBytes(input, 1);
    mode = atoi(input);
    
    switch (mode) {
      case 0:
        ping_loop();
        break;
      case 1:
        set_motor();
        break;
      default:
        break;
    }
  }
}
