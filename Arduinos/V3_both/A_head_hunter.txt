/* Minimal header/length probe for 1 kB-SRAM boards   */
/* Uses ONLY the built-in LED and Serial prints       */
/* Keeps <150 bytes global RAM                        */

#include "shared_constants.h"

const uint16_t EXPECTED_LEN = uint16_t(TOTAL_LEDS) * 3;   // 1206
const uint16_t BYTE_TIMEOUT = 300;                        // ms

/* timed read: returns -1 on timeout */
int rb() {
  unsigned long t0 = millis();
  while (!Serial.available())
    if (millis() - t0 > BYTE_TIMEOUT) return -1;
  return Serial.read();
}

void setup() {
  pinMode(13, OUTPUT); digitalWrite(13, LOW);   // heartbeat LED
  Serial.begin(BAUDRATE);
  Serial.println(F("\n=== header probe (SRAM-tiny) ==="));
}

uint32_t frame = 0;

void loop() {

  /* 1 ─ hunt for 0xAA 0x55 */
  int last = -1, cur = -1;
  while (true) {
    cur = rb(); if (cur < 0) { Serial.println(F("!! sync timeout")); return; }
    if (last == SYNC_1 && cur == SYNC_2) break;
    last = cur;
  }

  /* 2 ─ read 16-bit length */
  int lo = rb(), hi = rb();
  if (lo < 0 || hi < 0) { Serial.println(F("!! len timeout")); return; }
  uint16_t len = uint16_t(lo) | (uint16_t(hi) << 8);

  /* 3 ─ report */
  Serial.print(F("f#")); Serial.print(frame++);
  Serial.print(F(" len=")); Serial.print(len);
  if (len == EXPECTED_LEN) {
    Serial.println(F(" OK"));
    digitalWrite(13, HIGH); delay(20); digitalWrite(13, LOW);
  } else {
    Serial.println(F(" BAD"));
    digitalWrite(13, LOW);
  }

  /* 4 ─ discard payload + checksum (len+1) */
  uint32_t todo = uint32_t(len) + 1;
  while (todo--)
    if (rb() < 0) { Serial.println(F("!! payload timeout")); return; }
}
