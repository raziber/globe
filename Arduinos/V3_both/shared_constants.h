#pragma once
#include <stdint.h>

/* ---------- framing (Pi → AVR) -------------------------- */
constexpr uint8_t  SYNC_1   = 0xAA;
constexpr uint8_t  SYNC_2   = 0x55;
constexpr uint32_t BAUDRATE = 115200;

/* ---------- LED layout ---------------------------------- */
constexpr uint16_t TOTAL_LEDS = 402;
constexpr uint16_t NUM_LEDS_A = 220;                 // first segment
constexpr uint16_t NUM_LEDS_B = TOTAL_LEDS - NUM_LEDS_A;

/* ---------- GPIO pin ------------------------------------ */
constexpr uint8_t  LED_PIN = 6;                      // same on both AVRs
