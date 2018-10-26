#include "DualMC33926MotorShield.h"
#include <string.h>

DualMC33926MotorShield md;


//https://arduino.stackexchange.com/questions/1013/how-do-i-split-an-incoming-string
#define INPUT_SIZE 9

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
  // Get next command from Serial (add 1 for final 0)
  char input[INPUT_SIZE + 1];
  byte size = Serial.readBytes(input, INPUT_SIZE);
  // Add the final 0 to end the C string
  input[size] = 0;
  
  int lspeed = atoi(strtok(input, " "));
  int rspeed = atoi(strtok(NULL, " "));

  md.setM1Speed(lspeed);
  md.setM2Speed(rspeed);
}

void motor_setup()
{
  md.init();
}

