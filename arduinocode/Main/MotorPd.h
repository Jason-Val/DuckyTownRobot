#ifndef MotorPd_h
#define MotorPd_h

#include "Arduino.h"

class MotorPd
{
  public:
    MotorPd(double k, double b);
    double* computeCorrection(double* correction);
    void setC(double c);
    void resetInitPoint();
    void setVelocity();
  private:
    double K;
    double B;
    double encoderSegments;
    double dia;
    double WB;
    double C;
    double* v;
    double* sPrev;
    long tPrev;
    double prevError;
    double* buf;
    double* prevError2;
    double vref;

    double* getTranslation(double* trans);
    double* getVelocity(double* vel);
    double getPWM_l(double lRight);
    double getPWM_r(double vRight);
};

#endif
