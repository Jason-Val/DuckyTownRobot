#include <PinChangeInt.h>
#include <DualMC33926MotorShield.h>


#include <string.h>
#include "Robot.h"

#define INPUT_SIZE 32

DualMC33926MotorShield md;
void motor_setup();
void set_motor();
double ping_loop();
void ir_setup();
void get_ir();
void get_current();
void set_motor(double pwm_l, double pwm_r);
void set_motor_vel();


long time_since_pd_update = millis();
long time_since_ping_update = millis();
long pd_update_delay = 30;
long ping_update_delay = 200;

char terminate = ';';
char input[INPUT_SIZE + 1];

Robot robot;

void setup() {
  // initialize serial communication:
  Serial.begin(115200);
  ir_setup();
  md.init();
}

double read_velocity()
{
  byte num_bytes_read = Serial.readBytesUntil(terminate, input, INPUT_SIZE);
  // Add the final 0 to end the C string
  input[num_bytes_read] = 0;
  return atof(strtok(input, " "));
}

void loop() {
  int mode = -1;
  if (robot.isExecutingAction && millis() - time_since_pd_update > pd_update_delay) {
    robot.adjustHeading();
    time_since_pd_update = millis();
    if (robot.completedAction())
    {
      robot.notifyPi();
    }
  }
  // TODO* adding "false" here disables ping. remove it to re-enable
  if (millis() - time_since_ping_update > ping_update_delay) {
    robot.adjustVelWithPing(ping_loop());
    //Serial.print(robot.velIdeal);
    //Serial.print(", ");
    //Serial.println(robot.velActual);
    time_since_ping_update = millis();
  }
  
  if (Serial.available()) {
    char input[1];
    Serial.readBytes(input, 1);
    mode = atoi(input);
    
    switch (mode) {
      case 0:
        robot.driveStraight(read_velocity());
        break;
      case 1:
        robot.turnLeft(read_velocity());
        break;
      case 2:
        robot.turnRight(read_velocity());
        break;
      case 3:
        robot.adjustMotors(read_velocity());
        break;
      case 4:
        robot.velIdeal = read_velocity();
        break;
      case 5:
        robot.setMotors(read_velocity());
        break;
      case 6:
        Serial.println(robot.getHeading());
        break;
      case 7:
        robot.setHeading(read_velocity());
    }
  }
}
