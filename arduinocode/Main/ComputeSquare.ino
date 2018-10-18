
void compute_square_setup() {
  Serial.begin(9600);
}

void compute_square_loop() {
  if (Serial.available()) {
    float x = Serial.parseFloat();
    Serial.println(x*x);
  }
}
