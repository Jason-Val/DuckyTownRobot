#include "math.h"

#define PinMotor1Sensor1 5
#define PinMotor1Sensor2 6
#define PinMotor2Sensor1 2
#define PinMotor2Sensor2 3

volatile long right_count = 0;
volatile long left_count = 0;

extern Robot robot;

/*
int N_enc = 32; // Segments on Encoder = 32
double dia = 0.071; // Dia = 71 mm
double WB = 0.157;  // Wheel Base = 157 mm
double del_x, x, y, theta = 0.0;
double S_l = 0.0, S_r = 0.0;
*/

void ir_setup() {
  //Attach Interrupts
  attachPinChangeInterrupt(PinMotor1Sensor1, right_encoder_isr, CHANGE);
  attachPinChangeInterrupt(PinMotor1Sensor2, right_encoder_isr, CHANGE);
  attachPinChangeInterrupt(PinMotor2Sensor1, left_encoder_isr, CHANGE);
  attachPinChangeInterrupt(PinMotor2Sensor2, left_encoder_isr, CHANGE);
}

void get_ir() {
  Serial.println("2 " + String(left_count) + " " + String(right_count));
}

void right_encoder_isr() {
  static int8_t lookup_table_r[] = {0, -1, 1, 0, 1, 0, 0, -1, -1, 0, 0, 1, 0, 1, -1, 0};
  static uint8_t enc_val_r = 0;
  enc_val_r = enc_val_r << 2;
  enc_val_r = enc_val_r | ((PIND & 0b01100000) >> 5);
  right_count = right_count + lookup_table_r[enc_val_r & 0b1111];
  robot.updateLocation(left_count, right_count);
  //get_location();
}

void left_encoder_isr() {
  static int8_t lookup_table_l[] = {0, -1, 1, 0, 1, 0, 0, -1, -1, 0, 0, 1, 0, 1, -1, 0};
  static uint8_t enc_val_l = 0;
  enc_val_l = enc_val_l << 2;
  enc_val_l = enc_val_l | ((PIND & 0b00001100) >> 2);
  left_count = left_count + lookup_table_l[enc_val_l & 0b1111];
  robot.updateLocation(left_count, right_count);
  //get_location();
}
