#ifndef SHARED_CONSTANTS_H
#define SHARED_CONSTANTS_H

// Serial Communication
const long BAUDRATE = 115200;
const byte START_MARKER = 0xAA;
const byte END_MARKER = 0xBB;

// LED Configuration
const int TOTAL_LEDS = 402;
const int NUM_LEDS_A = 220; // Arduino A controls these
const int NUM_LEDS_B = TOTAL_LEDS - NUM_LEDS_A; // Arduino B controls the rest

const int LED_PIN_A = 6;
const int LED_PIN_B = 6;

// Calculated values
const int LED_DATA_SIZE = TOTAL_LEDS * 3; // 3 bytes per LED (R, G, B)

// Timeout for reading serial data (in milliseconds)
// Adjust as needed, should be longer than the time to receive a full packet
const unsigned long SERIAL_TIMEOUT_MS = 200;


#endif // SHARED_CONSTANTS_H