#include <Adafruit_NeoPixel.h>
#include "shared_constants.h"

// Which pin on the Arduino is connected to the NeoPixels?
// On Arduino A, this is defined in shared_constants.h as LED_PIN_A
// How many NeoPixels are attached to Arduino A?
// Defined in shared_constants.h as NUM_LEDS_A

Adafruit_NeoPixel stripA = Adafruit_NeoPixel(NUM_LEDS_A, LED_PIN_A, NEO_GRB + NEO_KHZ800);

byte serialBuffer[LED_DATA_SIZE + 5]; // Max possible packet size: START, LEN_H, LEN_L, DATA..., CHECKSUM, END
int bufferIndex = 0;
bool inPacket = false;
unsigned long lastByteTime = 0;

void setup() {
  Serial.begin(BAUDRATE);
  stripA.begin();           // INITIALIZE NeoPixel strip object (REQUIRED)
  stripA.show();            // Turn OFF all pixels ASAP
  stripA.setBrightness(50); // Set BRIGHTNESS to about 1/5 (max = 255) - ADJUST AS NEEDED
  // fillStrip(stripA.Color(0,0,0)); // Clear strip on startup
  // stripA.show();
}

byte calculate_buffer_checksum(const byte* data, int len_without_checksum_byte) {
  byte checksum = 0;
  for (int i = 0; i < len_without_checksum_byte; i++) {
    checksum ^= data[i];
  }
  return checksum;
}

void processPacket() {
  // Packet structure: START_MARKER, NUM_LEDS_H, NUM_LEDS_L, [DATA ...], CHECKSUM, END_MARKER
  // bufferIndex should be at least 5 (START, LEN_H, LEN_L, CHK, END) plus data
  if (bufferIndex < 5) { // Minimum packet parts
    // Serial.println("Packet too short.");
    return;
  }

  if (serialBuffer[0] != START_MARKER) {
    // Serial.println("Missing start marker.");
    return;
  }
  if (serialBuffer[bufferIndex - 1] != END_MARKER) {
    // Serial.println("Missing end marker.");
    return;
  }

  uint16_t packetNumLeds = (serialBuffer[1] << 8) | serialBuffer[2];
  
  if (packetNumLeds != TOTAL_LEDS) {
    // Serial.print("Packet LED count mismatch. Expected: ");
    // Serial.print(TOTAL_LEDS);
    // Serial.print(" Got: ");
    // Serial.println(packetNumLeds);
    return;
  }

  // Expected data length based on packetNumLeds
  int expectedDataLength = packetNumLeds * 3;
  // Actual data length in the buffer (excluding START, LEN_H, LEN_L, CHECKSUM, END)
  int actualDataLengthInBuffer = bufferIndex - 5; 

  if (expectedDataLength != actualDataLengthInBuffer) {
    // Serial.print("Data length mismatch. Expected data: ");
    // Serial.print(expectedDataLength);
    // Serial.print(" Got in buffer: ");
    // Serial.println(actualDataLengthInBuffer);
    return;
  }

  // Checksum is calculated over NUM_LEDS_H, NUM_LEDS_L, and DATA
  // The checksum byte itself is at serialBuffer[bufferIndex - 2]
  byte receivedChecksum = serialBuffer[bufferIndex - 2];
  byte calculatedChecksum = calculate_buffer_checksum(&serialBuffer[1], 2 + expectedDataLength); // 2 for LEN_H, LEN_L

  if (receivedChecksum != calculatedChecksum) {
    // Serial.print("Checksum mismatch. RX: ");
    // Serial.print(receivedChecksum, HEX);
    // Serial.print(" CALC: ");
    // Serial.println(calculatedChecksum, HEX);
    return;
  }

  // Packet is valid, update LEDs for Arduino A
  for (int i = 0; i < NUM_LEDS_A; i++) {
    int dataIdx = 3 + (i * 3); // Offset by 3 (START, LEN_H, LEN_L)
    if (dataIdx + 2 < bufferIndex - 2) { // Ensure we don't read past data into checksum/end
      byte r = serialBuffer[dataIdx];
      byte g = serialBuffer[dataIdx + 1];
      byte b = serialBuffer[dataIdx + 2];
      stripA.setPixelColor(i, stripA.Color(r, g, b));
    } else {
      // Data overrun, should not happen if lengths are checked
      break; 
    }
  }
  stripA.show();
  // Serial.println("Arduino A: Packet OK");
}


void loop() {
  while (Serial.available() > 0) {
    byte incomingByte = Serial.read();
    lastByteTime = millis(); // Update timestamp for timeout

    if (!inPacket) {
      if (incomingByte == START_MARKER) {
        inPacket = true;
        bufferIndex = 0;
        serialBuffer[bufferIndex++] = incomingByte;
      }
      // Else, discard bytes outside a packet
    } else { // We are in a packet
      if (bufferIndex < sizeof(serialBuffer)) {
        serialBuffer[bufferIndex++] = incomingByte;

        if (incomingByte == END_MARKER) {
          // Potentially complete packet
          if (bufferIndex > 4) { // Min: START, LEN_H, LEN_L, CHK, END
             uint16_t expectedNumLeds = (serialBuffer[1] << 8) | serialBuffer[2];
             int expectedPacketSize = 1 + 2 + (expectedNumLeds * 3) + 1 + 1; // START, LEN, DATA, CHK, END
             if (bufferIndex == expectedPacketSize) {
                processPacket();
             } else {
                // Serial.print("End marker received but length mismatch. Idx: ");
                // Serial.print(bufferIndex);
                // Serial.print(" Exp: ");
                // Serial.println(expectedPacketSize);
                // Corrupted packet or premature end marker, reset
             }
          } else {
            // Serial.println("End marker with too few bytes for header.");
            // Not a valid packet, reset
          }
          inPacket = false; // Reset for next packet
          bufferIndex = 0;
        }
      } else {
        // Buffer overflow! This should ideally not happen if RPi sends correct packets
        // And SERIAL_TIMEOUT_MS works.
        // Serial.println("Buffer overflow!");
        inPacket = false; // Reset to be safe
        bufferIndex = 0;
      }
    }
  } // end while Serial.available

  // Timeout check: if we are in a packet but haven't received a byte for too long
  if (inPacket && (millis() - lastByteTime > SERIAL_TIMEOUT_MS)) {
    // Serial.println("Serial receive timeout!");
    inPacket = false; // Reset packet state
    bufferIndex = 0;
  }
}

// Optional: Function to fill the strip with a color (useful for testing)
void fillStrip(uint32_t color) {
  for (int i = 0; i < stripA.numPixels(); i++) {
    stripA.setPixelColor(i, color);
  }
  stripA.show();
}