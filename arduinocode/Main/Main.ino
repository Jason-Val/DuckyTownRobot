#include <string.h>
#include "MotorPd.h"


void compute_square_loop();
void motor_setup();
void set_motor();
void ping_loop();
void ir_setup();
void get_ir();
void get_current();
void set_motor(double pwm_l, double pwm_r);

bool pd_active = false;
long t_pd_updated = millis();
long pd_update_delay = 1000;
MotorPd pd(1, 1);

void setup() {
  // initialize serial communication:
  Serial.begin(115200);
  motor_setup();
  ir_setup();
}

void loop() {
  motor_setup();
  int mode = -1;
  if (pd_active) {
    double *correction = new double[2];
    correction = pd.computeCorrection(correction);
    set_motor(correction[0], correction[1]);
  } 
  else if(millis() - t_pd_updated > pd_update_delay)
  {
    pd.resetInitPoint();
    t_pd_updated = millis();
  }
  
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
      case 3:
        pd_active = !pd_active;
      default:
        break;
    }
  }
}
