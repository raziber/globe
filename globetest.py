import openai
import requests
import pyttsx3
import speech_recognition as sr
from dotenv import load_dotenv
import os
import math
import json
import re
import time
import random

# Load environment variables
load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')
client = openai.OpenAI(api_key=api_key)

# Load LED layout
with open("led_layout.json") as f:
    leds = json.load(f)

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def get_voice_input(timeout=10):
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=timeout)
        except sr.WaitTimeoutError:
            return None
    try:
        print("Recognizing...")
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        return "Speech recognition service is down."

def get_weather(lat, lon):
    weather_api_key = os.getenv("WEATHER_API_KEY")
    if not weather_api_key:
        print("❌ No WEATHER_API_KEY loaded.")
        return None

    url = (
        f"https://api.openweathermap.org/data/2.5/weather?"
        f"lat={lat}&lon={lon}&appid={weather_api_key}&units=metric"
    )

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        weather = {
            "description": data["weather"][0]["description"],
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"]
        }
        return weather
    else:
        print(f"❌ Weather API error: {response.status_code} — {response.text}")
        return None

def get_combined_gpt_response(user_question, weather_summary=None):
    weather_note = (
        f"The current weather is: {weather_summary}\n\n" if weather_summary else ""
    )

    prompt = (
        f"You are a voice assistant. Your task is to answer user questions about places or regions.\n"
        f"Always return your response in exactly this format:\n\n"
        f"Location JSON:\n"
        f"```json\n"
        f"{{\n  \"type\": \"point\", \"lat\": ..., \"lon\": ..., \"color_rgb\": [R, G, B]\n}}\n"
        f"or\n"
        f"{{\n  \"type\": \"region\", \"polygon\": [[lat1, lon1], ...], \"color_rgb\": [R, G, B]\n}}\n"
        f"```\n\n"
        f"Answer:\n"
        f"(write a short, friendly spoken response that includes weather if available)\n\n"
        f"{weather_note}"
        f"Now, answer this user question in that exact format:\n"
        f"{user_question}"
    )

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    full_text = response.choices[0].message.content.strip()

    json_match = re.search(r"Location JSON:\s*```json\s*(\{.*?\})\s*```", full_text, re.DOTALL)
    answer_match = re.search(r"Answer:\s*(.+)", full_text, re.DOTALL)

    location_data = {}
    if json_match:
        try:
            location_data = json.loads(json_match.group(1))
        except json.JSONDecodeError:
            print("⚠️ Failed to parse JSON block.")
    else:
        print("⚠️ No Location JSON found.")

    spoken = answer_match.group(1).strip() if answer_match else "Sorry, I couldn't understand the location."
    return spoken, location_data

def spherical_from_latlon(lat, lon):
    theta = math.radians(lon)
    phi = math.radians(90 - lat)
    return theta, phi

def find_closest_led(theta, phi):
    min_dist = float("inf")
    closest_led = None
    for led in leds:
        dtheta = theta - led["theta"]
        dphi = phi - led["phi"]
        dist = math.sqrt(dtheta**2 + dphi**2)
        if dist < min_dist:
            min_dist = dist
            closest_led = led
    return closest_led

def find_leds_in_region(polygon, radius=0.2):
    led_ids = set()
    for theta, phi in polygon:
        for led in leds:
            dtheta = theta - led["theta"]
            dphi = phi - led["phi"]
            dist = math.sqrt(dtheta**2 + dphi**2)
            if dist < radius:
                led_ids.add(led["id"])
    return sorted(list(led_ids))

def process_location_data(location_data):
    color = location_data.get("color_rgb", [255, 255, 255])
    print(f"🎨 Color for highlight: RGB{tuple(color)}")

    if location_data.get("type") == "point":
        lat = location_data.get("lat")
        lon = location_data.get("lon")
        if lat is not None and lon is not None:
            theta, phi = spherical_from_latlon(lat, lon)
            closest_led = find_closest_led(theta, phi)
            location_data = {
                "type": "point",
                "theta": theta,
                "phi": phi,
                "color_rgb": color,
                "led_id": closest_led["id"]
            }
            print(f"Lighting LED #{closest_led['id']} at θ={theta:.2f}, ϕ={phi:.2f}")
        else:
            print("⚠️ Missing lat/lon for point.")

    elif location_data.get("type") == "region":
        polygon = location_data.get("polygon")
        spherical_polygon = []
        if polygon:
            print("Lighting region polygon:")
            for entry in polygon:
                if isinstance(entry, list) and len(entry) == 2 and all(isinstance(x, (int, float)) for x in entry):
                    lat, lon = entry
                    theta, phi = spherical_from_latlon(lat, lon)
                    spherical_polygon.append([theta, phi])
                    print(f"- Point: lat={lat}, lon={lon} → θ={theta:.2f}, ϕ={phi:.2f}")
                else:
                    print(f"⚠️ Skipped malformed entry: {entry}")
            region_leds = find_leds_in_region(spherical_polygon)
            location_data = {
                "type": "region",
                "polygon": spherical_polygon,
                "color_rgb": color,
                "led_ids": region_leds
            }
        else:
            print("⚠️ Region provided but no polygon found.")
    else:
        print("⚠️ Unknown location type.")

    print("📡 Spherical Location JSON:")
    print(json.dumps(location_data, indent=2))

def generate_idle_map(color_func):
    pixels = []
    for led in leds:
        theta, phi = led["theta"], led["phi"]
        color = color_func(theta, phi)
        pixels.append({"theta": theta, "phi": phi, "color_rgb": color})
    return {"type": "fullmap", "pixels": pixels}

def display_land_vs_water():
    def is_water(theta, phi):
        return phi > math.pi / 2  # crude water mask
    def color_func(theta, phi):
        return [0, 105, 148] if is_water(theta, phi) else [139, 69, 19]
    fullmap = generate_idle_map(color_func)
    print("🌊 Idle Mode: Land vs Water")
    print(json.dumps(fullmap, indent=2))

def display_day_night():
    def sun_direction():
        now = time.gmtime()
        lon_deg = (now.tm_hour + now.tm_min / 60.0) * 15 - 180
        return math.radians(lon_deg), math.radians(90)

    sun_theta, sun_phi = sun_direction()
    def color_func(theta, phi):
        brightness = math.cos(phi - sun_phi) * math.cos(theta - sun_theta)
        return [255, 255, 200] if brightness > 0.5 else [10, 10, 40]
    fullmap = generate_idle_map(color_func)
    print("🌗 Idle Mode: Day vs Night")
    print(json.dumps(fullmap, indent=2))

def display_altitude_map():
    def color_func(theta, phi):
        lat = 90 - math.degrees(phi)
        return [255, 0, 0] if lat > 45 else [0, 255, 0] if lat > 0 else [0, 0, 255]  # placeholder
    fullmap = generate_idle_map(color_func)
    print("🗻 Idle Mode: Altitude Map")
    print(json.dumps(fullmap, indent=2))

def idle_mode():
    print("🌙 Entering idle mode...")
    modes = [display_land_vs_water, display_day_night, display_altitude_map]
    i = 0

    while True:
        mode_func = modes[i % len(modes)]
        mode_func()
        i += 1

        for _ in range(10):
            voice_input = get_voice_input(timeout=1)
            if voice_input and "smart globe" in voice_input.lower():
                print("🟢 Wake word detected.")
                speak("How can I help?")
                return get_voice_input()
            elif voice_input:
                print("👂 Heard something, but not the wake word.")
            time.sleep(1)

def main():
    while True:
        user_input = get_voice_input(timeout=10)

        if user_input is None or user_input.strip() == "":
            user_input = idle_mode()

        if not user_input:
            continue

        print(f"You said: {user_input}")

        if user_input.startswith("Sorry"):
            speak(user_input)
            continue

        spoken_response, location_data = get_combined_gpt_response(user_input)

        if location_data:
            process_location_data(location_data)

        print(spoken_response)
        speak(spoken_response)

if __name__ == "__main__":
    main()
