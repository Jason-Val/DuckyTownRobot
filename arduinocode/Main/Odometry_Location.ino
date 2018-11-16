#include "math.h"

extern volatile long left_count;
extern volatile long right_count;
extern volatile long left_count;

int N_enc = 32;
double dia = 0.071; // Dia = 71 mm
double WB = 0.157;

double S_l;
double S_r;
double del_x;
double x;
double y;
double theta;
double loc[3];

void get_location()
{
  S_l = (M_PI*left_count*dia)/N_enc;
  S_r = (M_PI*right_count*dia)/N_enc;
  theta = atan2(((S_r - S_l) / 2.0), (WB / 2.0));
  del_x = (S_l + S_r) / 2;
  x = del_x * cos(theta);
  y = del_x * sin(theta);
  loc[0] = x;
  loc[1] = y;
  loc[2] = theta;
  Serial.print("  x:");
  Serial.print(x);
  Serial.print("  y:");
  Serial.print(y);
  Serial.print("  n_l:");
  Serial.print(left_count);
  Serial.print("  n_r:");
  Serial.print(right_count);
  Serial.print("  err_count:");
  Serial.print("  S_l:");
  Serial.print(S_l);
  Serial.print("  S_r:");
  Serial.println(S_r);
}
