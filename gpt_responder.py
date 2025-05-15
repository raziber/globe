import openai
import re
import json

class GPTResponder:
    def __init__(self, api_key):
        self.client = openai.OpenAI(api_key=api_key)

    def get_response(self, user_question, weather_summary=None):
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

        response = self.client.chat.completions.create(
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
