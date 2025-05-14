#include <FastLED.h>

#define NUM_LEDS 221
#define LED_PIN 6
#define DEBUG_LED 13

#define BYTES_TO_READ (NUM_LEDS * 3)

CRGB leds[NUM_LEDS];

void setup() {
  FastLED.addLeds<WS2812B, LED_PIN, RGB>(leds, NUM_LEDS);
  FastLED.setBrightness(100);

  pinMode(DEBUG_LED, OUTPUT);
  digitalWrite(DEBUG_LED, LOW);

  Serial.begin(115200);
}

void loop() {
  // === Wait for sync: 0xAA, 0x55 ===
  uint8_t lastByte = 0;
  bool synced = false;

  while (!synced) {
    if (Serial.available()) {
      uint8_t current = Serial.read();
      if (lastByte == 0xAA && current == 0x55) {
        synced = true;
        digitalWrite(DEBUG_LED, HIGH);  // Indicate sync found
      }
      lastByte = current;
    }
  }

  // === Skip 2 length bytes (0x04, 0xCB) ===
  while (Serial.available() < 2);  // wait until they exist
  Serial.read();  // skip len_hi
  Serial.read();  // skip len_lo

  // === Read 663 bytes (221 LEDs × 3) ===
  int received = 0;
  static uint8_t r, g, b;
  unsigned long start = millis();

  while (received < BYTES_TO_READ && millis() - start < 200) {
    if (Serial.available()) {
      uint8_t byte = Serial.read();
      int ledIndex = received / 3;
      int channel = received % 3;

      if (channel == 0) r = byte;
      else if (channel == 1) g = byte;
      else {
        b = byte;
        leds[ledIndex] = CRGB(r, g, b);
      }

      received++;
    }
  }

  if (received == BYTES_TO_READ) {
    FastLED.show();

    // Blink pin 13 LED after successful frame
    digitalWrite(DEBUG_LED, LOW);
    delay(5);
    digitalWrite(DEBUG_LED, HIGH);
    delay(5);
    digitalWrite(DEBUG_LED, LOW);
  }
}
