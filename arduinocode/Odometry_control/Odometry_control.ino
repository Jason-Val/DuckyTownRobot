#include "DualMC33926MotorShield.h"
#include "PinChangeInt.h"
#include "math.h"

// Update test 1

#define PinMotor1Sensor1 2
#define PinMotor1Sensor2 3
#define PinMotor2Sensor1 5
#define PinMotor2Sensor2 6

// Initialize:

// Constants:
double N_enc = 32.0; // Segments on Encoder = 32
double dia = 0.071; // Dia = 71 mm
double WB = 0.157;  // Wheel Base = 157 mm
int w1 = 2; // Weight factor right
int w2 = 1; //weight factor left
int flag = 0;

// Parameters:
int PWM_l;
int PWM_r;

// Variables:
int right_count = 0;
int left_count = 0;
int err_count = 0;
int n_l_ref = 0;
int n_r_ref = 0;
double del_x, x, y, theta = 0.0;
double S_l = 0.0, S_r = 0.0;
double loc[3];
double S_l_ref, S_r_ref;

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
  first_stretch();
  /*
    if (flag == 0) {
      first_stretch();
    }
    else if (flag == 1) {
      curved_path();
    }
    else if (flag == 2) {
      second_stretch();
    }
    else {
      Serial.println("Broken Flag");
      Serial.end();
    }
  */
  //else if (flag == 1)
  //{
  //curve_path();
  //}
  //curve_path();
  //Serial.println("Right:" + String(left_count) + " Left:" + String(right_count) + "; S_l=" + String(S_l) + " S_r=" + String(S_r) + "; theta:" + String(theta * (180.0 / M_PI)));
  //Serial.println(Etime);
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

void left_encoder_isr() {
  static int8_t lookup_table_r[] = {
    0, -1, 1, 0, 1, 0, 0, -1, -1, 0, 0, 1, 0, 1, -1, 0
  };
  static uint8_t enc_val_r = 0;
  enc_val_r = enc_val_r << 2;
  enc_val_r = enc_val_r | ((PIND & 0b00001100) >> 2);
  left_count = left_count + lookup_table_r[enc_val_r & 0b1111];
}

void right_encoder_isr() {
  static int8_t lookup_table_l[] = {
    0, -1, 1, 0, 1, 0, 0, -1, -1, 0, 0, 1, 0, 1, -1, 0
  };
  static uint8_t enc_val_l = 0;
  enc_val_l = enc_val_l << 2;
  enc_val_l = enc_val_l | ((PIND & 0b01100000) >> 5);
  //    Serial.println(enc_val_l);
  right_count = right_count + lookup_table_l[enc_val_l & 0b1111];
}

void get_location() {
  left_encoder_isr();
  right_encoder_isr();
  err_count = (right_count - left_count);
  S_l = ((M_PI * dia * left_count) / N_enc);
  S_r = ((M_PI * dia * right_count) / N_enc);
  theta = atan2(((S_r - S_l) / 2.0), (WB / 2.0));
  del_x = (S_l + S_r) / 2;
  x = del_x * cos(theta);
  y = del_x * sin(theta);
  loc[0] = x;
  loc[1] = y;
  loc[2] = theta;
  Serial.print("  n_l:");
  Serial.print(left_count);
  Serial.print("  n_r:");
  Serial.print(right_count);
  Serial.print("  err_count:");
  Serial.print(err_count);
  Serial.print("  S_l:");
  Serial.print(S_l);
  Serial.print("  S_r:");
  Serial.println(S_r);
}

/*
  void set_refcounts() {
  n_l_ref = (N_enc * S_l_ref) / (M_PI * dia);
  n_r_ref = (N_enc * S_r_ref) / (M_PI * dia);
  }
*/

void motor_control() {
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
    flag = flag + 1;
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

void first_stretch() {
  PWM_l = 200;
  PWM_r = 200;
  S_l_ref = 0.5;
  S_r_ref = 0.5;
  get_location();
  if (err_count >= 0) {
    PWM_l = PWM_l + w1 * (err_count);
    PWM_r = PWM_r - w1 * (err_count);
  }
  else {
    PWM_l = PWM_l - w2 * (err_count);
    PWM_r = PWM_r + w2 * (err_count);
  }
  motor_control();
}

void curved_path() {
  PWM_l = 200;
  PWM_r = 290;
  S_l_ref = 0.83 / 2;
  S_r_ref = 0.57 / 2;
  get_location();
  motor_control();
  /*
    if (left_count > right_count) {
    PWM_l = PWM_l - w * (err_count);
    }
    else if (right_count > left_count) {
    PWM_r = PWM_r - w * (err_count);
    }
  */
}

void second_stretch() {
  PWM_l = 200;
  PWM_r = 200;
  S_l_ref = 1.0;
  S_r_ref = 1.0;
  get_location();
  if (err_count >= 0) {
    PWM_l = PWM_l + w1 * (err_count);
    PWM_r = PWM_r - w1 * (err_count);
  }
  else {
    PWM_l = PWM_l - w2 * (err_count);
    PWM_r = PWM_r + w2 * (err_count);
  }
  motor_control();
}
