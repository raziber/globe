"""
Raspberry-Pi 4B LED Test Script.
This script tests the WS2815 LED strip.
The data pin is connected to pin 12 - GPIO 18 of the Raspberry Pi 4B.
"""

import time
from rpi_ws281x import PixelStrip, Color

# LED strip configuration:
LED_COUNT = 50        # Number of LED pixels.
LED_PIN = 18          # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 50   # Set to 0 for darkest and 255 for brightest
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

# Create PixelStrip object with appropriate configuration.
strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
# Initialize the library (must be called once before other functions).
strip.begin()

# Simple test: Turn all LEDs red for 2 seconds, then off
print("Testing LEDs - turning all red...")
for i in range(strip.numPixels()):
    strip.setPixelColor(i, Color(255, 0, 0))  # Red
strip.show()
time.sleep(2)

print("Turning LEDs off...")
for i in range(strip.numPixels()):
    strip.setPixelColor(i, Color(0, 0, 0))  # Off
strip.show()

print("LED test complete.")

