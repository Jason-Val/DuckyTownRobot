#include "Arduino.h"
#include "Robot.h"
#include "math.h"

Robot::Robot()
{
  K = 120.0;
  B = 0.5;
  encoderSegments = 32;
  wheelDiameter = 0.071;
  wheelBase = 0.157;
  C = 1.0;
  velIdeal = 0.0;
  velActual = 0.0;
  isExecutingAction = false;
  distanceToTravel = 0;
  loc = new double[3];
  translation = new double[2];
  startTranslation = new double[2];
  prevError = 0.0;
}


bool Robot::completedAction()
{
  if (!(translation[0] - startTranslation[0] < distanceToTravel) && !(translation[1]  - startTranslation[1] < distanceToTravel))
  {
    isExecutingAction = false;
    return true;
  }
  else
  {
    return false;
  }
}

void Robot::notifyPi()
{
  Serial.println("1");
}

void Robot::driveStraight(double velocity)
{
  isExecutingAction = true;
  C = 1.0;
  distanceToTravel = 1;
  velIdeal = velocity;
  //md.setSpeeds(200, 200); //TODO: base this off of velocity
  updateStartTranslation();
}

void Robot::turnLeft(double velocity)
{
  isExecutingAction = true;
  C = 2.4;
  distanceToTravel = 0.75;
  velIdeal = velocity;
  //md.setSpeeds(200, 200);
  updateStartTranslation();
}

void Robot::turnRight(double velocity)
{
  isExecutingAction = true;
  C = -3.0;
  distanceToTravel = 0.35;
  velIdeal = velocity;
  //md.setSpeeds(150, 150); //TODO: base this off of velocity
  updateStartTranslation();
}

void Robot::setMotors(double velocity)
{
  velIdeal = velocity;
  velActual = velocity;
  md.setSpeeds(convertVelToPWM_L(velocity), convertVelToPWM_R(velocity));
}

// The main computation for the visual-based pd control. It simply
// applies the calculations performed by the pi
void Robot::adjustMotors(double velocity)
{
  md.setSpeeds(convertVelToPWM_L(velActual + velocity), convertVelToPWM_L(velActual - velocity));
}

void Robot::adjustVelWithPing()
{
  velActual = velIdeal; //TODO: decrease velActual if necessary
}

// The main computation for the encoder-based pd control
void Robot::adjustHeading()
{
  double error = translation[0] - C*translation[1];
  double errorDot = error - prevError;
  prevError = error;
  double deltaPWM = K*error + B*errorDot;
  md.setSpeeds(convertVelToPWM_L(velActual) + deltaPWM, convertVelToPWM_L(velActual) - deltaPWM);
}

void Robot::updateLocation(long leftCount, long rightCount)
{
  translation[0] = ((M_PI * wheelDiameter * leftCount) / encoderSegments);
  translation[1] = ((M_PI * wheelDiameter * rightCount) / encoderSegments);

  double theta = atan2(((translation[1] - translation[0]) / 2.0), (wheelBase / 2.0));
  double del_x = (translation[0] + translation[1]) / 2;
  
  loc[0] = del_x * cos(theta);
  loc[1] = del_x * sin(theta);
  loc[2] = theta;
}

void Robot::updateStartTranslation()
{
  startTranslation[0] = translation[0];
  startTranslation[1] = translation[1];
}

//TODO: finish these
double Robot::convertVelToPWM_L(double velocity)
{
  if (velocity == 0)
  {
    return 0;
  }
  return 670.29*velocity + 82.878;
}
double Robot::convertVelToPWM_R(double velocity)
{
  if (velocity == 0)
  {
    return 0;
  }
  return 658.57*velocity + 77.307;
}
