import math
import json
import time
import os
import random
from playsound import playsound
import threading
from socket_connection import send_to_socket

# Global socket connection variables
writer = None
sock = None


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
        global writer, sock
        success, writer, sock = send_to_socket(output, writer, sock)

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
            global writer, sock
            success, writer, sock = send_to_socket(output, writer, sock)

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
        global writer, sock
        success, writer, sock = send_to_socket(output, writer, sock)

    def display_day_night_animated(self, duration=30, frame_rate=5):
        """
        Animate the Earth's rotation: day/night changes over time.
        :param duration: total animation time in seconds
        :param frame_rate: number of frames per second
        """
        print("🌍 Animated Day/Night Terminator Starting...")
        start_time = time.time()
        total_frames = duration * frame_rate
        frame_delay = 1.0 / frame_rate

        while time.time() - start_time < duration:
            elapsed = time.time() - start_time
            sun_lon_deg = ((elapsed / duration) * 360.0 - 180.0) % 360
            sun_phi = math.radians(sun_lon_deg)
            sun_theta = math.radians(90)  # Equator sun position

            def color_func(theta, phi):
                brightness = math.cos(phi - sun_phi) * math.cos(theta - sun_theta)
                if brightness > 0.5:
                    return [255, 255, 180]  # Day
                elif brightness > 0:
                    return [80, 80, 100]    # Twilight
                else:
                    return [10, 10, 40]     # Night

            output = self.generate_idle_map(color_func)
            global writer, sock
            success, writer, sock = send_to_socket(output, writer, sock)

            # Check for wake word interrupt
            if self.voice_interface:
                voice_input = self.voice_interface.listen(timeout=0.2)
                if voice_input and "smart globe" in voice_input.lower():
                    print("🟢 Wake word detected during animation.")
                    self.voice_interface.speak("How can I help?")
                    return self.voice_interface.listen(timeout=10)

            time.sleep(frame_delay)
            
    def display_land_vs_water_animated(self, duration=30, frame_rate=5):
        """
        Pulsing animation between land and water using brightness waves.
        :param duration: how long to run (seconds)
        :param frame_rate: how many updates per second
        """
        print("🌊 Animated Land/Water Pulse Starting...")
        start_time = time.time()
        frame_delay = 1.0 / frame_rate

        def is_water(theta, phi):
            # Replace this with real map data later
            return phi > math.pi / 2  # crude placeholder

        while time.time() - start_time < duration:
            elapsed = time.time() - start_time
            wave = (math.sin(elapsed * math.pi * 2 / 5) + 1) / 2  # cycles every 5 seconds (0–1)

            def color_func(theta, phi):
                if is_water(theta, phi):
                    base = [0, 105, 148]  # water blue
                else:
                    base = [139, 69, 19]  # land brown

                # Apply wave brightness scaling
                return [int(c * (0.5 + 0.5 * wave)) for c in base]

            output = self.generate_idle_map(color_func)
            global writer, sock
            success, writer, sock = send_to_socket(output, writer, sock)

            # Wake word check
            if self.voice_interface:
                voice_input = self.voice_interface.listen(timeout=0.2)
                if voice_input and "smart globe" in voice_input.lower():
                    print("🟢 Wake word detected during land/water animation.")
                    self.voice_interface.speak("How can I help?")
                    return self.voice_interface.listen(timeout=10)

            time.sleep(frame_delay)

    def display_lightning_storms(self, duration=30, frame_rate=10, flash_probability=0.02):
        """
        Simulate animated lightning strikes on the globe.
        :param duration: total duration in seconds
        :param frame_rate: updates per second
        :param flash_probability: chance for each LED to flash per frame
        """
        print("⚡ Lightning Strike Animation Starting...")
        start_time = time.time()
        frame_delay = 1.0 / frame_rate

        while time.time() - start_time < duration:
            pixels = []

            for led in self.leds:
                theta = led["theta"]
                phi = led["phi"]

                # Crude fake storm zone: between phi=π/2 and 3π/2
                in_storm_zone = math.pi/2 < phi < 3*math.pi/2

                flash = in_storm_zone and random.random() < flash_probability
                if flash:
                    color = [255, 255, 255]  # Lightning white
                    # ⚡ Sound cue (non-blocking)
                    threading.Thread(target=playsound, args=("lightning.wav",), daemon=True).start()
                else:
                    color = [10, 10, 30]  # Night blue

                pixels.append({
                    "id": led["id"],
                    "theta": theta,
                    "phi": phi,
                    "color_rgb": color
                })

            output = {
                "type": "fullmap",
                "pixels": pixels
            }

            global writer, sock
            success, writer, sock = send_to_socket(output, writer, sock)

            # Wake word check
            if self.voice_interface:
                voice_input = self.voice_interface.listen(timeout=0.1)
                if voice_input and "smart globe" in voice_input.lower():
                    print("🟢 Wake word detected during lightning.")
                    self.voice_interface.speak("How can I help?")
                    return self.voice_interface.listen(timeout=10)

            time.sleep(frame_delay)

    def run_idle_loop(self, voice_interface):
        print("🌙 Entering idle mode...")
        self.voice_interface = voice_interface

        # List of modes with durations
        modes = [
            (self.display_land_vs_water_animated, 20),
            (self.display_day_night_animated, 30),
            (self.display_altitude_map, 15),  # static mode, no animation loop
            (self.display_lightning_storms, 15)
        ]

        i = 0
        while True:
            mode_func, duration = modes[i % len(modes)]
            print(f"🔁 Switching to idle mode: {mode_func.__name__} for {duration}s")

            # Run animated or static mode
            try:
                if mode_func.__code__.co_argcount == 2:
                    # Function expects a duration (self, duration)
                    result = mode_func(duration=duration)
                else:
                    # Function expects only self
                    mode_func()
                    time.sleep(duration)
                    result = None
            except Exception as e:
                print(f"⚠️ Error running idle mode: {e}")
                result = None

            # If wake word was triggered
            if result:
                return result

            i += 1


