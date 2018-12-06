#include "DualMC33926MotorShield.h"
#include "PinChangeInt.h"
#include "math.h"

#define PinMotor1Sensor1 5
#define PinMotor1Sensor2 6
#define PinMotor2Sensor1 2
#define PinMotor2Sensor2 3

// Constants:
int N_enc = 32; // Segments on Encoder = 32
double dia = 0.071; // Dia = 71 mm
double WB = 0.157;  // Wheel Base = 157 mm
int w1 = 10; // Weight factor right
int w2 = 4; //weight factor left
int flag = 0;

// Parameters:
int PWM_l;
int PWM_r;

// Variables:
volatile long right_count = 0;
volatile long left_count = 0;
volatile long err_count = 0;
int n_l_ref = 0;
int n_r_ref = 0;
double S_l = 0.0, S_r = 0.0;
double S_l_ref, S_r_ref;

DualMC33926MotorShield md;

void setup() 
{
  Serial.begin(115200);
  md.init();
  
  attachPinChangeInterrupt(PinMotor1Sensor1, right_encoder_isr, CHANGE);
  attachPinChangeInterrupt(PinMotor1Sensor2, right_encoder_isr, CHANGE);
  
  //  attachInterrupt(digitalPinToInterrupt(PinMotor2Sensor1), left_encoder_isr, CHANGE);
  attachPinChangeInterrupt(PinMotor2Sensor1, left_encoder_isr, CHANGE);
  attachPinChangeInterrupt(PinMotor2Sensor2, left_encoder_isr, CHANGE);
  }

void loop() {
  //left_encoder_isr();
  //right_encoder_isr();
  err_count = (right_count - left_count);
  S_l = ((M_PI * dia * left_count) / N_enc);
  S_r = ((M_PI * dia * right_count) / N_enc);

  if ((S_l < 1.0)&&(S_r < 1.0)){
  PWM_l = 150;
  PWM_r = 150;
  
  PWM_l = PWM_l + w1 * err_count;
  PWM_r = PWM_r - w2 * err_count;
  
  Serial.print(" PWM_l = ");
  Serial.print(PWM_l);
  Serial.print(" PWM_r = ");
  Serial.print(PWM_r);
  Serial.print(" n_l = ");
  Serial.print(left_count);
  Serial.print(" n_r = ");
  Serial.print(right_count);
  Serial.print(" err_count = ");
  Serial.println(err_count);
  
  md.setM1Speed(PWM_l); //Left
  md.setM2Speed(PWM_r); //Right
  }
  else{
  md.setM1Speed(0); //Left
  md.setM2Speed(0); //Right
  Serial.end();
  }
  //delay(20);
}

void right_encoder_isr() {
  static int8_t lookup_table_r[] = {0, -1, 1, 0, 1, 0, 0, -1, -1, 0, 0, 1, 0, 1, -1, 0};
  static uint8_t enc_val_r = 0;
  enc_val_r = enc_val_r << 2;
  enc_val_r = enc_val_r | ((PIND & 0b01100000) >> 5);
  right_count = right_count + lookup_table_r[enc_val_r & 0b1111];
}

void left_encoder_isr() {
  static int8_t lookup_table_l[] = {0, -1, 1, 0, 1, 0, 0, -1, -1, 0, 0, 1, 0, 1, -1, 0};
  static uint8_t enc_val_l = 0;
  enc_val_l = enc_val_l << 2;
  enc_val_l = enc_val_l | ((PIND & 0b00001100) >> 2);
  left_count = left_count + lookup_table_l[enc_val_l & 0b1111];
}
