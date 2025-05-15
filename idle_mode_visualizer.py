import math
import json
import time

class IdleModeVisualizer:
    def __init__(self, leds):
        self.leds = leds

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
        print(json.dumps(self.generate_idle_map(color_func), indent=2))

    def display_day_night(self):
        def sun_direction():
            now = time.gmtime()
            lon_deg = (now.tm_hour + now.tm_min / 60.0) * 15 - 180
            return math.radians(lon_deg), math.radians(90)

        sun_theta, sun_phi = sun_direction()

        def color_func(theta, phi):
            brightness = math.cos(phi - sun_phi) * math.cos(theta - sun_theta)
            return [255, 255, 200] if brightness > 0.5 else [10, 10, 40]

        print("🌗 Idle Mode: Day vs Night")
        print(json.dumps(self.generate_idle_map(color_func), indent=2))

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
        print(json.dumps(self.generate_idle_map(color_func), indent=2))

    def run_idle_loop(self, voice_interface):
        print("🌙 Entering idle mode...")
        modes = [self.display_land_vs_water, self.display_day_night, self.display_altitude_map]
        i = 0

        while True:
            mode_func = modes[i % len(modes)]
            mode_func()
            i += 1

            for _ in range(10):
                voice_input = voice_interface.listen(timeout=1)
                if voice_input and "smart globe" in voice_input.lower():
                    print("🟢 Wake word detected.")
                    voice_interface.speak("How can I help?")
                    return voice_input
                elif voice_input:
                    print("👂 Heard something, but not the wake word.")
                time.sleep(1)
