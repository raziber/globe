#include <FastLED.h>

#define NUM_LEDS 188
#define LED_PIN 6
#define DEBUG_LED 13

#define START_INDEX 221
#define BYTES_TO_SKIP (START_INDEX * 3)
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
  // Wait for 4-byte header: 0xAA 0x55 [length_hi] [length_lo]
  bool synced = false;
  while (!synced) {
    if (Serial.available() >= 4) {
      if (Serial.read() == 0xAA && Serial.read() == 0x55) {
        uint8_t len_hi = Serial.read();
        uint8_t len_lo = Serial.read();
        int expected_len = (len_hi << 8) | len_lo;
        if (expected_len == 409 * 3) {
          synced = true;
          digitalWrite(DEBUG_LED, HIGH);
        }
      }
    }
  }

  // Skip Arduino A’s bytes
  int skipped = 0;
  while (skipped < BYTES_TO_SKIP) {
    if (Serial.available()) {
      Serial.read();
      skipped++;
    }
  }

  // Read and display Arduino B's portion
  int received = 0;
  static uint8_t r, g, b;
  while (received < BYTES_TO_READ) {
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

  FastLED.show();

  // Flash pin 13 LED for debug
  digitalWrite(DEBUG_LED, LOW);
  delay(5);
  digitalWrite(DEBUG_LED, HIGH);
  delay(5);
  digitalWrite(DEBUG_LED, LOW);
}
