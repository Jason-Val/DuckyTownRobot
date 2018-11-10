#include "DualMC33926MotorShield.h"
#include "PinChangeInt.h"
#include "math.h"

#define PinMotor1Sensor1 2
#define PinMotor1Sensor2 3
#define PinMotor2Sensor1 5
#define PinMotor2Sensor2 6

// Initialize:

// Constants:
double K = 1.0;
double B = 1.0;
double V_ref = 0.25;
double N_enc = 32.0;   // Segments on Encoder = 32
double dia = 0.068;  // Dia = 68 mm
double WB = 0.157;   // Wheel Base = 157 mm

// Variables:
volatile long right_count = 0.0;
volatile long left_count = 0.0;
double Etime;
double del_x, x, y, theta = 0.0;
double S_l, S_r = 0.0;
double err = 0.0, V_l, V_r, del_V = 0.0;
double err_dot = 0.0;
double loc[3];
double PWM_ref_l, PWM_ref_r, PWM_l, PWM_r;
double C;

long time_start = 0;
double S_l_start = 0;
double S_r_start = 0;

DualMC33926MotorShield md;

void setup()
{
  Etime = millis();
  Serial.begin(115200);
  md.init();
  //Attach Interrupts
  attachPinChangeInterrupt(PinMotor1Sensor1, right_encoder_isr, CHANGE);
  attachPinChangeInterrupt(PinMotor1Sensor2, right_encoder_isr, CHANGE);

  attachPinChangeInterrupt(PinMotor2Sensor1, left_encoder_isr, CHANGE);
  attachPinChangeInterrupt(PinMotor2Sensor2, left_encoder_isr, CHANGE);

  PWM_ref_r = 675.09*V_ref + 79.807;
  PWM_ref_l = 695.55*V_ref + 66.464;

  //md.setM1Speed(PWM_ref_l); //Left
  //md.setM2Speed(PWM_ref_r); //Right
  
  delay(2000);
  
  left_encoder_isr();
  right_encoder_isr();
  time_start = millis();
  get_location();
  delay(1000);
  get_velocity();
   Serial.println("; V_l =" + String(V_l) + " ;V_r =" + String(V_r));
   Serial.println("Exit setup");
   delay(2000);
   
   delay(1000);
}

void loop()
{
  /*
  Etime = millis();
  delay(1000);
  left_encoder_isr();
  right_encoder_isr();
  get_location();
  time_start = Etime;
  get_velocity();
  motor_PDcontrol();
  delay(10);
  //Serial.println("Right:" + String(left_count) + " Left:" + String(right_count) + "; V_l=" + String(V_l) + " V_r=" + String(V_r) + "; theta:" + String(theta * (180.0 / M_PI)) + "err =" + String(err)+ "err_dot =" + String(err_dot));
  //Serial.println(Etime);
  */
  get_location();
  Serial.println("Left: " + String(S_l));
  Serial.println("Right: " + String(S_r));
}

void get_location()
{
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

void update_location()
{
  S_l_start = ((M_PI * dia * left_count) / N_enc);
  S_r_start = ((M_PI * dia * right_count) / N_enc);
}

void get_velocity() {
  //V_l = (S_l / (Etime / 1000));
  //V_r = (S_r / (Etime / 1000));
  Serial.println("sl: " + String(S_l) + "; slstart: " + String(S_l_start));
  Serial.println("sr: " + String(S_r) + "; srstart: " + String(S_r_start));
  double delta_s_l = S_l - S_l_start;
  double delta_s_r = S_r - S_r_start;

  long delta_time = (millis() - time_start)/1000;
  V_l = delta_s_l/delta_time;
  V_r = delta_s_r/delta_time;
  time_start = millis();
  update_location();
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


void motor_PDcontrol() {
  C = 1.0;
  err = V_r-C*V_l;
  err_dot = err - err_dot;
  del_V = -K*(err)-B*(err_dot);
  Serial.print(" n_l =" + String(left_count) + "n_r =" + String(right_count) + "err = " + String(err));
  Serial.print("; err_dot = " + String(err_dot));
  Serial.print("; V_l =" + String(V_l) + " ;V_r =" + String(V_r) + "; del_V =" + String(del_V));
  err_dot = err;
 
  V_l = V_l + del_V/2.0;
  V_r = V_r - del_V/2.0;

  Serial.print("; V_lnew =" + String(V_l) + " ;V_rnew =" + String(V_r));
  
  PWM_r = 675.09*V_r + 79.807;
  PWM_l = 695.55*V_l + 66.464;

  Serial.println("; PWM_l =" + String(PWM_l) + " ;PWM_r =" + String(PWM_r));

  //md.setM1Speed(PWM_l); //Left
  //md.setM2Speed(PWM_r); //Right

  md.setM1Speed(0); //Left
  md.setM2Speed(0); //Right

  
}
