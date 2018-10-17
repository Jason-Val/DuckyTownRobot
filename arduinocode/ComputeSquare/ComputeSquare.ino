void setup() {
  // initialize serial communication:
  Serial.begin(9600);
  Serial.println("Hello pi!");
}

void loop()
{
  if (Serial.available()) {
    float x = Serial.parseFloat();
    Serial.println(x*x);
  }
}
