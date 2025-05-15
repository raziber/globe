import math
import json
import time
import os

OUTPUT_FILE = "led_output.json"

def write_led_output(data):
    with open(OUTPUT_FILE, "w") as f:
        json.dump(data, f, indent=2)
    print(f"💾 Wrote {len(data['pixels'])} idle pixels to {OUTPUT_FILE}")


class IdleModeVisualizer:
    def __init__(self, leds):
        self.leds = leds
        self.voice_interface = None  # will be set from run_idle_loop()

    def generate_idle_map(self, color_func):
        pixels = []
        for led in self.leds:
            theta = led["theta"]
            phi = led["phi"]
            color = color_func(theta, phi)
            pixels.append({
                "id": led["id"],
                "theta": theta,
                "phi": phi,
                "color_rgb": color
            })
        return {"type": "fullmap", "pixels": pixels}

    def display_land_vs_water(self):
        def is_water(theta, phi):
            return phi > math.pi / 2  # crude fake logic

        def color_func(theta, phi):
            return [0, 105, 148] if is_water(theta, phi) else [139, 69, 19]

        print("🌊 Idle Mode: Land vs Water")
        output = self.generate_idle_map(color_func)
        write_led_output(output)

    def display_day_night(self, duration=30, step_seconds=1):
        def sun_direction(shift_deg):
            lon_deg = shift_deg - 180
            return math.radians(lon_deg), math.radians(90)

        print("🌗 Idle Mode: Animated Day/Night Terminator")
        start_time = time.time()
        while time.time() - start_time < duration:
            elapsed = time.time() - start_time
            shift_deg = (elapsed / duration) * 360

            sun_theta, sun_phi = sun_direction(shift_deg)

            def color_func(theta, phi):
                brightness = math.cos(phi - sun_phi) * math.cos(theta - sun_theta)
                return [255, 255, 200] if brightness > 0.5 else [10, 10, 40]

            output = self.generate_idle_map(color_func)
            write_led_output(output)

            for _ in range(step_seconds):
                if self.voice_interface:
                    voice_input = self.voice_interface.listen(timeout=1)
                    if voice_input and "smart globe" in voice_input.lower():
                        print("🟢 Wake word detected (during animation).")
                        self.voice_interface.speak("How can I help?")
                        return self.voice_interface.listen(timeout=10)
                time.sleep(1)

    def display_altitude_map(self):
        def color_func(theta, phi):
            lat = 90 - math.degrees(phi)
            if lat > 45:
                return [255, 0, 0]
            elif lat > 0:
                return [0, 255, 0]
            else:
                return [0, 0, 255]

        print("🗻 Idle Mode: Altitude Map")
        output = self.generate_idle_map(color_func)
        write_led_output(output)

    def run_idle_loop(self, voice_interface):
        print("🌙 Entering idle mode...")
        self.voice_interface = voice_interface

        modes = [self.display_land_vs_water, self.display_day_night, self.display_altitude_map]
        i = 0

        while True:
            mode_func = modes[i % len(modes)]
            result = mode_func()
            if result:
                return result  # exit early with user command
            i += 1

            for _ in range(10):
                voice_input = voice_interface.listen(timeout=1)
                if voice_input and "smart globe" in voice_input.lower():
                    print("🟢 Wake word detected.")
                    voice_interface.speak("How can I help?")
                    while True:
                        command_input = voice_interface.listen(timeout=10)
                        if command_input:
                            print(f"🎙️ Received command: {command_input}")
                            return command_input
                        else:
                            print("⏳ Waiting for user command...")
                elif voice_input:
                    print("👂 Heard something, but not the wake word.")
                time.sleep(1)
