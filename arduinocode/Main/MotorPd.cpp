#include "Arduino.h"
#include "MotorPd.h"
#include "math.h"

#define INPUT_SIZE 32

extern volatile long right_count;
extern volatile long left_count;


/*
long* getCounts(long* counts)
{
  
  cli();
  counts[0] = left_count;
  counts[1] = right_count;
  sei();
}
*/
/*
long* getCounts(long* counts)
{
  uint8_t SaveSREG = SREG;   // save interrupt flag
  cli();   // disable interrupts
  counts[0] = left_count;
  counts[1] = right_count;
  SREG = SaveSREG;   // restore the interrupt flag
  return counts;
}
*/
double* MotorPd::getTranslation(double* trans)
{
  trans[0] = ((M_PI * dia * left_count) / encoderSegments);
  trans[1] = ((M_PI * dia * right_count) / encoderSegments);
  //Serial.print(trans[0]);
  //Serial.print(", ");
  //Serial.println(trans[1]);
  return trans;
}

MotorPd::MotorPd(double k, double b)
{
  encoderSegments = 32.0;
  dia = 0.068;
  WB = 0.157;
  C = 1.0;
  
  K = k;
  B = b;
  sPrev = new double[2];
  sPrev = getTranslation(sPrev);
  v = new double[2];
  v[0] = 0;
  v[1] = 0;
  tPrev = millis();
  prevError = 0;
  prevError2 = new double[2];
  prevError2[0] = 0;
  prevError2[1] = 0;
  buf = new double[2];
  vref = 0;
}

void MotorPd::setVelocity()
{
  char terminate = ';';
  char input[INPUT_SIZE + 1];
  byte size = Serial.readBytesUntil(terminate, input, INPUT_SIZE);
  
  // Add the final 0 to end the C string
  input[size] = 0;
  
  float lspeed = atof(strtok(input, " "));
  float rspeed = atof(strtok(NULL, " "));
  
  v[0] = lspeed;
  v[1] = rspeed;
  vref = lspeed;
}

double* MotorPd::getVelocity(double* vel)
{
  buf = getTranslation(buf);
  long t = millis();
  double delta_t = ((double)(t - tPrev))/1000.0;
  buf[0] = (buf[0] - sPrev[0])/delta_t;
  buf[1] = (buf[1] - sPrev[1])/delta_t;
  return buf;
}

void MotorPd::resetInitPoint()
{
  
  //double* vel = new double[2];
  //vel = getVelocity(vel);
  
  //Serial.print(vel[0]);
  //Serial.print(", ");
  //Serial.println(vel[1]);
  //Serial.print("counts: ");
  //Serial.print(left_count);
  //Serial.print(", ");
  //Serial.println(right_count);
  
  sPrev = getTranslation(sPrev);
  tPrev = millis();
}

void MotorPd::setC(double c)
{
  C = c;
}

double MotorPd::getPWM_r(double vRight)
{
  if (vRight == 0)
  {
    return 0;
  }
  return 695.55*vRight + 66.464;
}

double MotorPd::getPWM_l(double vLeft)
{
  if (vLeft == 0)
  {
    return 0;
  }
  return 675.09*vLeft + 79.807;
}
/*
double* MotorPd::computeCorrection(double* correction)
{
  double* vNew = getVelocity(buf);
  
  double* error = new double[2];
  error[0] = vNew[1]-C*vNew[0];
  error[1] = vNew[0] + vNew[1] - 2*vref;
  
  double* deltaError = new double[2];
  deltaError[0] = error[0] - prevError2[0];
  deltaError[1] = error[1] - prevError2[1];
  
  prevError2[0] = error[0];
  prevError2[1] = error[1];
  double* deltaV = new double[2];
  deltaV[0] = -K*(error[0])-B*(deltaError[0]);
  deltaV[1] = -K*(error[1])-B*(deltaError[1]);
  
  Serial.print("; velocity: ");
  Serial.print(vNew[0]);
  Serial.print(", ");
  Serial.println(vNew[1]);
  
  vNew[0] = vNew[0] + (-deltaV[0]/2.0 + deltaV[1]);
  vNew[1] = vNew[1] + (deltaV[0]/2.0 + deltaV[1]);

  correction[0] = getPWM_l(vNew[0]);
  correction[1] = getPWM_r(vNew[1]);
  
  return correction;
}
*/
/*
double* MotorPd::computeCorrection(double* correction)
{
  double* vNew = getVelocity(buf);
  
  double* vIdeal = new double[2];
  vIdeal[0] = 2*C*vref/(C+1);
  vIdeal[1] = 2*vref/(C+1);
  
  double* error = new double[2];
  error[0] = vIdeal[0] - vNew[0];
  error[1] = vIdeal[1] - vNew[1];
  
  double* deltaError = new double[2];
  deltaError[0] = error[0] - prevError2[0];
  deltaError[1] = error[1] - prevError2[1];
  
  prevError2[0] = error[0];
  prevError2[1] = error[1];
  double* deltaV = new double[2];
  deltaV[0] = -K*(error[0])-B*(deltaError[0]);
  deltaV[1] = -K*(error[1])-B*(deltaError[1]);

  //Serial.print("; velocity: ");
  //Serial.print(vNew[0]);
  //Serial.print(", ");
  //Serial.println(vNew[1]);
  
  vNew[0] = vNew[0] - deltaV[0];
  vNew[1] = vNew[1] - deltaV[1];

  correction[0] = getPWM_l(vNew[0]);
  correction[1] = getPWM_r(vNew[1]);
  
  return correction;
}
*/
/*
double* MotorPd::computeCorrection(double* correction)
{
  double* vNew = getVelocity(buf);
  
  double* error = new double[2];
  error[0] = v[0] - vNew[0];
  error[1] = v[1] - vNew[1];
  
  double* deltaError = new double[2];
  deltaError[0] = error[0] - prevError2[0];
  deltaError[1] = error[1] - prevError2[1];
  
  prevError2[0] = error[0];
  prevError2[1] = error[1];
  double* deltaV = new double[2];
  deltaV[0] = -K*(error[0])-B*(deltaError[0]);
  deltaV[1] = -K*(error[1])-B*(deltaError[1]);
  
  
  Serial.print("error: ");
  Serial.print(error[0]);
  Serial.print("; deltaError: ");
  Serial.print(deltaError[0]);
  Serial.print("; deltaV: ");
  Serial.print(deltaV[0]);
  Serial.print("; velocity: ");
  Serial.print(vNew[0]);
  Serial.print(", ");
  Serial.println(vNew[1]);
  
  vNew[0] = vNew[0] - deltaV[0];
  vNew[1] = vNew[1] - deltaV[1];
  
  Serial.print("; new velocity: ");
  Serial.print(vNew[0]);
  Serial.print(", ");
  Serial.println(vNew[1]);
  
  correction[0] = getPWM_l(vNew[0]);
  correction[1] = getPWM_r(vNew[1]);
  
  return correction;
}
*/

double* MotorPd::computeCorrection(double* correction)
{
  double* vNew = getVelocity(buf);
  
  
  double error = vNew[1]-C*vNew[0];
  double deltaError = error - prevError;
  prevError = error;
  double deltaV = -K*(error)-B*(deltaError);
  
  Serial.print("error: ");
  Serial.print(error);
  Serial.print("; deltaError: ");
  Serial.print(deltaError);
  Serial.print("; deltaV: ");
  Serial.print(deltaV);
  Serial.print("; velocity: ");
  Serial.print(vNew[0]);
  Serial.print(", ");
  Serial.println(vNew[1]);
  
  v[0] = vNew[0] - deltaV;
  v[1] = vNew[1] + deltaV;
  
  Serial.print("; new velocity: ");
  Serial.print(v[0]);
  Serial.print(", ");
  Serial.println(v[1]);
  
  correction[0] = getPWM_l(v[0]);
  correction[1] = getPWM_r(v[1]);
  
  return correction;
}


