#include "DualMC33926MotorShield.h"
#include <string.h>

DualMC33926MotorShield md;


//https://arduino.stackexchange.com/questions/1013/how-do-i-split-an-incoming-string
#define INPUT_SIZE 32

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
  char terminate = '.';
  char input[INPUT_SIZE + 1];
  byte size = Serial.readBytesUntil(terminate, input, INPUT_SIZE);
  
  // Add the final 0 to end the C string
  input[size] = 0;
  
  int lspeed = atoi(strtok(input, " "));
  int rspeed = atoi(strtok(NULL, " "));

  md.setSpeeds(lspeed, rspeed);
}

void get_current()
{
  Serial.println(String(md.getM1CurrentMilliamps()) + ", " + String(md.getM2CurrentMilliamps()));
}

void motor_setup()
{
  md.init();
}
