#include <PinChangeInt.h>

#include <DualMC33926MotorShield.h>


#include "math.h"

#define PinMotor1Sensor1 2
#define PinMotor1Sensor2 3
#define PinMotor2Sensor1 5
#define PinMotor2Sensor2 6

// Initialize:

// Constants:
double K = 1.0;
double B = 1.0;
double S_ref = 0.6096;
double N_enc = 32.0;   // Segments on Encoder = 32
double dia = 0.071;  // Dia = 71 mm
double WB = 0.157;   // Wheel Base = 157 mm

// Variables:
double right_count = 0.0;
double left_count = 0.0;
double n_ref = 0.0;
double del_x, x, y, theta = 0.0;
double S_l, S_r = 0.0;
double loc[3];

DualMC33926MotorShield md;

void setup()
{
  Serial.begin(115200);
  md.init();
  //Attach Interrupts
  attachPinChangeInterrupt(PinMotor1Sensor1, right_encoder_isr, CHANGE);
  attachPinChangeInterrupt(PinMotor1Sensor2, right_encoder_isr, CHANGE);

  attachPinChangeInterrupt(PinMotor2Sensor1, left_encoder_isr, CHANGE);
  attachPinChangeInterrupt(PinMotor2Sensor2, left_encoder_isr, CHANGE);

}

void loop()
{
  left_encoder_isr();
  right_encoder_isr();
  get_location();
  set_location();
  motor_control();
  //Serial.println("Right:" + String(left_count) + " Left:" + String(right_count) + "; S_l=" + String(S_l) + " S_r=" + String(S_r) + "; theta:" + String(theta * (180.0 / M_PI)));
  //Serial.println(Etime);
  delay(1000);
  //Serial.print("S_ref: " + String(S_ref) + "; n_ref: " + String(n_ref));
  //Serial.println("; S_l: " + String(S_l) + "; S_r: " + String(S_r) + "; n_l: " + String(left_count) +"; n_r:" + String(right_count));
}

void get_location() {
  S_l = ((M_PI * dia * left_count) / N_enc);
  S_r = ((M_PI * dia * right_count) / N_enc);
  theta = atan2(((S_r - S_l) / 2.0), (WB / 2.0));
  del_x = (S_l + S_r) / 2;
  x = del_x * cos(theta);
  y = del_x * sin(theta);
  loc[0] = x;
  loc[1] = y;
  loc[2] = theta;
}

void set_location() {
  n_ref = (N_enc*S_ref)/(M_PI * dia);
}

void right_encoder_isr() {
  static int8_t lookup_table_r[] = {0, -1, 1, 0, 1, 0, 0, -1, -1, 0, 0, 1, 0, 1, -1, 0};
  static uint8_t enc_val_r = 0;
  enc_val_r = enc_val_r << 2;
  enc_val_r = enc_val_r | ((PIND & 0b00001100) >> 2);
  right_count = right_count + lookup_table_r[enc_val_r & 0b1111];
}

void left_encoder_isr() {
  static int8_t lookup_table_l[] = {0, -1, 1, 0, 1, 0, 0, -1, -1, 0, 0, 1, 0, 1, -1, 0};
  static uint8_t enc_val_l = 0;
  enc_val_l = enc_val_l << 2;
  enc_val_l = enc_val_l | ((PIND & 0b01100000) >> 5);
  //    Serial.println(enc_val_l);
  left_count = left_count + lookup_table_l[enc_val_l & 0b1111];
}

void motor_control() {

  if (((left_count < (n_ref-20))||(right_count < (n_ref-20)))||((left_count < (n_ref-20))||(right_count < (n_ref-20)))){
    md.setM1Speed(200); //Left
    md.setM2Speed(200); //Right
  }
  else{
    md.setM1Speed(0); //Left
    md.setM2Speed(0); //Right  
  }
}
