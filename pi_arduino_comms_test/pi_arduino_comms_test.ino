void setup() {
  Serial.begin(9600);
}

void loop() {
  if (Serial.available()) {
    String msg = Serial.readStringUntil('\n');
    Serial.print("You said: ");
    Serial.println(msg);
  }
}
