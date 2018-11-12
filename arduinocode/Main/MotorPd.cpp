#include "Arduino.h"
#include "MotorPd.h"
#include "math.h"

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
  long* counts = new long[2];
  //counts = getCounts(counts);
  trans[0] = ((M_PI * dia * left_count) / encoderSegments);
  trans[1] = ((M_PI * dia * right_count) / encoderSegments);
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
}

double* MotorPd::getVelocity(double* vel)
{
  double* currentS = new double[2];
  currentS = getTranslation(currentS);
  long t = millis();
  double delta_t = ((double)(t - tPrev))/1000.0;
  vel[0] = (currentS[0] - sPrev[0])/delta_t;
  vel[1] = (currentS[1] - sPrev[1])/delta_t;
  return vel;
}

void MotorPd::resetInitPoint()
{
  
  //double* vel = new double[2];
  //vel = getVelocity(vel);
  
  //long* counts = new long[2];
  //counts = getCounts(counts);
  //Serial.print(vel[0]);
  //Serial.print(", ");
  //Serial.println(vel[1]);
  Serial.print("counts: ");
  Serial.print(left_count);
  Serial.print(", ");
  Serial.println(right_count);
  
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

double* MotorPd::computeCorrection(double* correction)
{
  double* vNew = new double[2];
  vNew = getVelocity(vNew);
  resetInitPoint();
  
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
  
  v[0] = vNew[0] - deltaV/2.0;
  v[1] = vNew[1] + deltaV/2.0;
  
  Serial.print("; new velocity: ");
  Serial.print(v[0]);
  Serial.print(", ");
  Serial.println(v[1]);
  
  correction[0] = getPWM_l(v[0]);
  correction[1] = getPWM_r(v[1]);
  
  return correction;
}
