void setup() {
  Serial.begin(9600);         // For UART communication with Pi
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
  if (Serial.available()) {
    String msg = Serial.readStringUntil('\n');

    // Blink LED on receive
    digitalWrite(LED_BUILTIN, HIGH);
    delay(200);
    digitalWrite(LED_BUILTIN, LOW);

    // Optional: echo back to Pi or Serial Monitor
    Serial.print("Received: ");
    Serial.println(msg);
  }
}
