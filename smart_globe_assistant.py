import json
from dotenv import load_dotenv
import os

from voice_interface import VoiceInterface
from gpt_responder import GPTResponder
from location_processor import LocationProcessor
from idle_mode_visualizer import IdleModeVisualizer

class SmartGlobeAssistant:
    def __init__(self, led_layout_path):
        load_dotenv()
        self.voice = VoiceInterface()
        self.gpt = GPTResponder(api_key=os.getenv("OPENAI_API_KEY"))

        with open(led_layout_path) as f:
            leds = json.load(f)

        self.processor = LocationProcessor(leds)
        self.visualizer = IdleModeVisualizer(leds)

    def run(self):
        while True:
            user_input = self.voice.listen(timeout=10)

            if user_input is None or user_input.strip() == "":
                user_input = self.visualizer.run_idle_loop(self.voice)

            if not user_input:
                continue

            print(f"You said: {user_input}")

            if user_input.startswith("Sorry"):
                self.voice.speak(user_input)
                continue

            spoken_response, location_data = self.gpt.get_response(user_input)

            if location_data:
                result = self.processor.process_location(location_data)
                print("📡 Processed location data:")
                print(json.dumps(result, indent=2))

            print(spoken_response)
            self.voice.speak(spoken_response)
