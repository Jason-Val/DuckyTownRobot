#ifndef Robot_h
#define Robot_h

#include "Arduino.h"
#include <DualMC33926MotorShield.h>

class Robot
{
  public:
    bool isExecutingAction;
    double velIdeal;
    double velActual;
    
    Robot();
    void adjustHeading();
    void setHeading(double heading);
    void adjustVelWithPing(double dist);
    bool completedAction();
    double getHeading();
    void driveStraight(double velocity);
    void turnLeft(double velocity);
    void turnRight(double velocity);
    void adjustMotors(double velocity);
    void notifyPi();
    void updateLocation(long leftCount, long rightCount);
    void setMotors(double velocity);
  private:
    double K;
    double B;
    double prevError;
    double encoderSegments;
    double wheelDiameter;
    double wheelBase;
    double C;
    double headingOffset;
    //double velActual;
    double distanceToTravel;
    double* loc;
    double* translation;
    double* startTranslation;
    DualMC33926MotorShield md;
    double lastAdjustment;
    double *newTranslation;

    void updateStartTranslation();
    double convertVelToPWM_L(double velocity);
    double convertVelToPWM_R(double velocity);
};

#endif
