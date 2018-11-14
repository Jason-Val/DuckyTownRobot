#include <string.h>

DualMC33926MotorShield md;


//https://arduino.stackexchange.com/questions/1013/how-do-i-split-an-incoming-string
#define INPUT_SIZE 32
/*
double getPWM_r(double vRight)
{
  if (vRight == 0)
  {
    return 0;
  }
  return 695.55*vRight + 66.464;
}

double getPWM_l(double vLeft)
{
  if (vLeft == 0)
  {
    return 0;
  }
  return 675.09*vLeft + 79.807;
}
*/
double getPWM_r(double vRight)
{
  if (vRight == 0)
  {
    return 0;
  }
  return 695.55*vRight + 66.464;
}

double getPWM_l(double vLeft)
{
  if (vLeft == 0)
  {
    return 0;
  }
  //return 675.09*vLeft + 79.807;
  return 665.09*vLeft + 79.807;
  //return 650.09*vLeft + 79.807;
}

void stopIfFault()
{
  if (md.getFault())
  {
    //Serial.println("fault");
    //Serial.flush();
    while(1);
  }
}

void set_motor()
{
  char terminate = ';';
  char input[INPUT_SIZE + 1];
  byte size = Serial.readBytesUntil(terminate, input, INPUT_SIZE);
  
  // Add the final 0 to end the C string
  input[size] = 0;
  
  int lspeed = atoi(strtok(input, " "));
  int rspeed = atoi(strtok(NULL, " "));
  md.setSpeeds(lspeed, rspeed);
}

void set_motor_vel()
{
  char terminate = ';';
  char input[INPUT_SIZE + 1];
  byte size = Serial.readBytesUntil(terminate, input, INPUT_SIZE);
  
  // Add the final 0 to end the C string
  input[size] = 0;
  
  float lspeed = atof(strtok(input, " "));
  float rspeed = atof(strtok(NULL, " "));
  
  md.setSpeeds(getPWM_l(lspeed), getPWM_r(rspeed));
}

void set_motor(double pwm_l, double pwm_r)
{
  md.setSpeeds(pwm_l, pwm_r);
}

void get_current()
{
  Serial.println(String(md.getM1CurrentMilliamps()) + ", " + String(md.getM2CurrentMilliamps()));
}

void motor_setup()
{
  md.init();
}
