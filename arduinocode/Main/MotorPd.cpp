#include "Arduino.h"
#include "MotorPd.h"

extern volatile long right_count;
extern volatile long left_count;

double* MotorPd::getTranslation(double* trans)
{
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
  v[1] = 1;
  tPrev = millis();
  prevError = 0;
}

double* MotorPd::getVelocity(double* vel)
{
  double* currentS = new double[2];
  currentS = getTranslation(currentS);
  long t = millis();
  vel[0] = (currentS[0] - sPrev[0])/(t - tPrev);
  vel[1] = (currentS[1] - sPrev[1])/(t - tPrev);
  
  return vel;
}

void MotorPd::resetInitPoint()
{
  sPrev = getTranslation(sPrev);
  tPrev = millis();
}

void MotorPd::setC(double c)
{
  C = c;
}

double MotorPd::getPWM_l(double vLeft)
{
  return 695.55*vLeft + 66.464;
}

double MotorPd::getPWM_r(double vRight)
{
  return 675.09*vRight + 79.807;
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
  v[0] += deltaV/2.0;
  v[1] -= deltaV/2.0;
  correction[0] = getPWM_l(v[0]);
  correction[1] = getPWM_r(v[1]);
  
  return correction;
}
