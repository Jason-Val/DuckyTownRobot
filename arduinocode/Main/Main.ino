#include <string.h>
#include <DualMC33926MotorShield.h>
#include <PinChangeInt.h>
#include "MotorPd.h"


void compute_square_loop();
void motor_setup();
void set_motor();
void ping_loop();
void ir_setup();
void get_ir();
void get_current();
void set_motor(double pwm_l, double pwm_r);
void set_motor_vel();
void get_location();

bool pd_active = false;
long t_pd_updated = millis();
long pd_update_delay = 30;
MotorPd pd(0.3, -.1);
//MotorPd pd(200, -100);
double* correction = new double[2];

extern volatile long right_count;
extern volatile long left_count;

void setup() {
  // initialize serial communication:
  Serial.begin(115200);
  motor_setup();
  ir_setup();
}

void loop() {
  int mode = -1;
  if (pd_active && millis() - t_pd_updated > pd_update_delay) {
    correction = pd.computeCorrection(correction);
    set_motor(correction[0], correction[1]);
    pd.resetInitPoint();
    t_pd_updated = millis();
  }
  else if(millis() - t_pd_updated > pd_update_delay)
  {
    pd.resetInitPoint();
    t_pd_updated = millis();
  }

  /*
  if (user_started)
  {
    if(flagged1)
    {
      flagged1 = firststretc();
      if (!flagged1) {
        flagged2 = true;
      }
    }
    if(flagged2)
    {
      flagged2 = curve();
      if(!flagged2)
      {
        flagged3=true;
      }
    }
    if(flaggd3)
    {
      flagged3 = secondstrecth();
      if(!flagged3)
      {
        user_started=false;
      }
    }
  }
  

  if(flag1)
  {
    flag1=firststrecht();
    delay(100);
  }
  */
  
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
      case 2:
        get_ir();
        break;
      case 3:
        pd_active = !pd_active;
        break;
      case 4:
        //set_motor_vel();
        pd.setVelocity();
        //delay(500);
        break;
      case 5:
        set_motor_vel();
        break;
      case 6:
        get_location();
      default:
        break;
    }
  }
}
