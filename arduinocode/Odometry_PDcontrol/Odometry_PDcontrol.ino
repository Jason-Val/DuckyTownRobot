#include "DualMC33926MotorShield.h"
#include "PinChangeInt.h"
#include "math.h"

// Update test 1

#define PinMotor1Sensor1 5
#define PinMotor1Sensor2 6
#define PinMotor2Sensor1 2
#define PinMotor2Sensor2 3

// Initialize:

// Constants:
int N_enc = 32; // Segments on Encoder = 32
double dia = 0.071; // Dia = 71 mm
double WB = 0.157;  // Wheel Base = 157 mm
double C;
double K = 120.0;
double B = 0.5;

// Parameters:
int PWM_l;
int PWM_r;

// Variables:
volatile long right_count = 0;
volatile long left_count = 0;
long err_count = 0;
int n_l_ref = 0;
int n_r_ref = 0;
double del_x, x, y, theta = 0.0;
double S_l = 0.0, S_r = 0.0;
double loc[3];
double S_l_ref, S_r_ref, err_S, errdot_S, err_temp = 0.0, del_S;

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
  //go_straight();
  right_turn();
  //left_turn();
  delay(10);
  Serial.print("  n_l:");
  Serial.print(left_count);
  Serial.print("  n_r:");
  Serial.print(right_count);
  Serial.print("  S_l:");
  Serial.print(S_l);
  Serial.print("  S_r:");
  Serial.print(S_r);
  Serial.print("  err_S:");
  Serial.print(err_S);
  Serial.print("  errdot_S:");
  Serial.println(errdot_S);
  //get_location();
  /*
    delay(1000);
    Serial.print("S_l:");
    Serial.print(S_l);
    Serial.print("  S_r:");
    Serial.print(S_r);
    Serial.print("  n_l:");
    Serial.print(left_count);
    Serial.print("  n_r:");
    Serial.print(right_count);
    Serial.print("  PWM_l:");
    Serial.print(PWM_l);
    Serial.print("  PWM_r:");
    Serial.print(PWM_r);
    Serial.print("  err_count:");
    Serial.println(err_count);
  */
}

void right_encoder_isr() {
  static int8_t lookup_table_r[] = {0, -1, 1, 0, 1, 0, 0, -1, -1, 0, 0, 1, 0, 1, -1, 0};
  static uint8_t enc_val_r = 0;
  enc_val_r = enc_val_r << 2;
  enc_val_r = enc_val_r | ((PIND & 0b01100000) >> 5);
  right_count = right_count + lookup_table_r[enc_val_r & 0b1111];
  get_location();
}

void left_encoder_isr() {
  static int8_t lookup_table_l[] = {0, -1, 1, 0, 1, 0, 0, -1, -1, 0, 0, 1, 0, 1, -1, 0};
  static uint8_t enc_val_l = 0;
  enc_val_l = enc_val_l << 2;
  enc_val_l = enc_val_l | ((PIND & 0b00001100) >> 2);
  //    Serial.println(enc_val_l);
  left_count = left_count + lookup_table_l[enc_val_l & 0b1111];
  get_location();
}

void get_location() {
  //left_encoder_isr();
  //right_encoder_isr();
  //err_count = (right_count - left_count);
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

void check_point() {
  if ((S_l < S_l_ref) && (S_r < S_r_ref)) {
    throttle();
    //delay(100);
    Serial.print("  PWM_l:");
    Serial.print(PWM_l);
    Serial.print("  PWM_r:");
    Serial.print(PWM_r);
  }
  else {
    brake();
    Serial.end();
  }
}

void throttle() {
  md.setM1Speed(PWM_l); //Left
  md.setM2Speed(PWM_r); //Right
}

void brake() {
  md.setM1Speed(0); //Left
  md.setM2Speed(0); //Right
}

void go_straight() {
  C = 1.0;
  PWM_l = 200;
  PWM_r = 200;
  S_l_ref = 1.0;
  S_r_ref = 1.0;
  
  PD_controller();
}

void right_turn() {
  C = -3.0;
  PWM_l = 150;
  PWM_r = 150;
  S_l_ref = 0.35;
  S_r_ref = 0.35;
  
  PD_controller();
}

void left_turn() {
  C = 2.4;
  PWM_l = 200;
  PWM_r = 200;
  S_l_ref = 0.75;
  S_r_ref = 0.75;
  
  PD_controller();
}

void PD_controller(){
  errdot_S = err_temp;
  err_S = S_r - C*S_l;
  err_temp = err_S;
  del_S = K*err_S+B*errdot_S;
  
  PWM_l = PWM_l + del_S;
  PWM_r = PWM_r - del_S;
  check_point();
}
