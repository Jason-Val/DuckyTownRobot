
void compute_square_loop() {
  while (!Serial.available()) {
  }
  if (Serial.available()) {
    float x = Serial.parseFloat();
    Serial.println(x*x);
    Serial.flush();
  }
}
