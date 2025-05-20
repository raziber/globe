#include <FastLED.h>
#include "shared_constants.h"

/* ========================================================
   !!  SET THESE LINES BEFORE EACH BUILD / UPLOAD         !!
   --------------------------------------------------------
   Arduino-A → MY_OFFSET = 0            , MY_LEDCOUNT = NUM_LEDS_A
   Arduino-B → MY_OFFSET = NUM_LEDS_A   , MY_LEDCOUNT = NUM_LEDS_B
   =======================================================*/
#define MY_OFFSET     0                  // 0 for A, NUM_LEDS_A for B
#define MY_LEDCOUNT   NUM_LEDS_A         // NUM_LEDS_A for A, NUM_LEDS_B for B
/* =======================================================*/

CRGB leds[MY_LEDCOUNT];

inline uint8_t readBlocking() { 
  // Add a timeout to prevent hanging
  unsigned long startTime = millis();
  while (!Serial.available()) {
    if (millis() - startTime > 1000) { // 1 second timeout
      return 0; // Return 0 on timeout
    }
  }
  return Serial.read(); 
}

/* hunt for 0xAA 0x55 */
void waitForSync() {
    uint8_t last = 0;
    for (;;) {
        uint8_t b = readBlocking();
        if (last == SYNC_1 && b == SYNC_2) { digitalWrite(13, HIGH); return; }
        last = b;
    }
}

void setup() {
    pinMode(13, OUTPUT);  digitalWrite(13, LOW);
    FastLED.addLeds<WS2812B, LED_PIN, RGB>(leds, MY_LEDCOUNT);
    FastLED.setBrightness(120);
    Serial.begin(BAUDRATE);
}

void loop() {
    /* 1 ─ locate frame start */
    waitForSync();

    /* 2 ─ read length (little-endian) */
    uint16_t len  =  readBlocking();          // low byte
              len |= readBlocking() << 8;     // high byte
    const uint16_t EXPECTED_LEN = TOTAL_LEDS * 3;   // 1206
    if (len != EXPECTED_LEN) {                // bad header
        for (uint16_t i = 0; i < len && i < 1000; ++i) readBlocking(); // Added safety limit
        return;
    }

    /* 3 ─ skip bytes that precede my segment */
    for (uint32_t i = 0; i < (uint32_t)MY_OFFSET * 3; ++i) readBlocking();

    /* 4 ─ read my LEDs */
    for (uint16_t i = 0; i < MY_LEDCOUNT; ++i) {
        uint8_t r = readBlocking();
        uint8_t g = readBlocking();
        uint8_t b = readBlocking();
        leds[i] = CRGB(r, g, b);
    }
    FastLED.show();

    /* heartbeat */
    digitalWrite(13, LOW);  delay(40);
    digitalWrite(13, HIGH); delay(40);
    digitalWrite(13, LOW);

    /* 5 ─ discard remaining bytes - COMPLETELY FIXED */
    // For Arduino A, this is the safer calculation:
    uint16_t payload_remaining = 0;
    
    // If you're Arduino A (MY_OFFSET = 0), then you need to discard:
    // (TOTAL_LEDS - NUM_LEDS_A) * 3 bytes
    if (MY_OFFSET == 0) {
        // Explicit calculation - calculate the number of bytes to discard directly
        payload_remaining = (TOTAL_LEDS - MY_LEDCOUNT) * 3;
    } 
    else {
        // Original calculation, with safety check
        uint32_t bytes_processed = (uint32_t)(MY_OFFSET + MY_LEDCOUNT) * 3;
        if (bytes_processed < len) {
            payload_remaining = len - bytes_processed;
        }
    }
    
    // Add a safety limit to prevent very long loops if calculation is wrong
    if (payload_remaining > EXPECTED_LEN) {
        payload_remaining = 0;
    }
    
    // Discard remaining bytes with timeout protection
    for (uint16_t i = 0; i < payload_remaining; ++i) {
        readBlocking();
    }

    /* 6 ─ consume checksum byte */
    (void)readBlocking();
}