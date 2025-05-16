import os
import json
import re
from openai import OpenAI

class GPTHandler:
    def __init__(self, api_key=None):
        """
        Initialize the GPT handler for generating responses to globe-related queries.
        
        Args:
            api_key (str): OpenAI API key. If not provided, it will look for OPENAI_API_KEY env variable.
        """
        # Use provided API key or get from environment
        if api_key is None:
            api_key = os.environ.get("OPENAI_API_KEY")
            if api_key is None:
                raise ValueError(
                    "OpenAI API key not found. Please provide an API key or set the OPENAI_API_KEY environment variable."
                )
        
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4.1-mini"  # Default model, can be changed
        print("GPT handler initialized.")

    def set_model(self, model_name):
        """
        Set a different OpenAI model to use.
        
        Args:
            model_name (str): The name of the OpenAI model to use.
        """
        self.model = model_name
        print(f"Model set to: {self.model}")

    def create_prompt(self, user_question, weather_summary=None):
        """
        Create the prompt for GPT based on the user's question and optional weather data.
        
        Args:
            user_question (str): The user's query about a location or region
            weather_summary (str, optional): Current weather information if available
            
        Returns:
            str: Formatted prompt for OpenAI API
        """
        weather_note = (
            f"The current weather is: {weather_summary}\n\n" if weather_summary else ""
        )

        prompt = (
            f"You are an interactive globe voice assistant. Your task is to answer user questions about places or regions on earch.\n you should strive to be as accurate as possible but still nive and not overly cautious.\n"
            f"Always return your response in exactly this format:\n\n"
            f"Location JSON:\n"
            f"```json\n"
            f"{{\n  \"type\": \"point\", \"lat\": ..., \"lon\": ..., \"color_rgb\": [R, G, B]\n}}\n"
            f"or\n"
            f"{{\n  \"type\": \"region\", \"polygon\": [[lat1, lon1], ...], \"color_rgb\": [R, G, B]\n}}\n"
            f"```\n\n"
            f"Answer:\n"
            f"(write a short, friendly spoken response that includes weather if available, do not exceed 1 sentence)\n\n"
            f"{weather_note}"
            f"Now, answer this user question in that exact format:\n"
            f"{user_question}"
        )
        
        return prompt

    def get_response(self, user_question, weather_summary=None):
        """
        Get a response from OpenAI for the user's globe-related query.
        
        Args:
            user_question (str): The user's query about a location or region
            weather_summary (str, optional): Current weather information if available
            
        Returns:
            tuple: (location_data, answer_text)
                - location_data: Dictionary with location info (type, coordinates, color)
                - answer_text: The text response to be spoken to the user
        """
        prompt = self.create_prompt(user_question, weather_summary)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Extract the response content
            response_content = response.choices[0].message.content
            
            # Parse the response to extract JSON and answer
            location_data = self._extract_location_json(response_content)
            answer_text = self._extract_answer_text(response_content)
            
            return location_data, answer_text
            
        except Exception as e:
            print(f"Error getting response from OpenAI: {e}")
            return None, f"I'm sorry, I couldn't process your request. {str(e)}"
    
    def _extract_location_json(self, response_content):
        """Extract and parse the location JSON from the response"""
        try:
            # Look for JSON block between ```json and ```
            json_match = re.search(r'```json\s*(.*?)\s*```', response_content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                return json.loads(json_str)
            else:
                print("No JSON found in the response")
                return None
        except Exception as e:
            print(f"Error parsing location JSON: {e}")
            return None
    
    def _extract_answer_text(self, response_content):
        """Extract the answer text from the response"""
        try:
            # Look for text after "Answer:" and before any new section or end of string
            answer_match = re.search(r'Answer:\s*(.*?)(?:\n\n|$)', response_content, re.DOTALL)
            if answer_match:
                return answer_match.group(1).strip()
            else:
                print("No answer text found in the response")
                return "I couldn't find the information you're looking for."
        except Exception as e:
            print(f"Error extracting answer text: {e}")
            return "I'm sorry, I couldn't process that information."


# Test function to verify functionality
def test():
    # First check if API key is set
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("WARNING: OPENAI_API_KEY environment variable not set. Testing will fail.")
        print("Please set your OpenAI API key with:")
        print('$env:OPENAI_API_KEY = "your-api-key"')
        return

    handler = GPTHandler()
    test_question = "Tell me about Paris, France"
    print(f"Testing with question: {test_question}")
    
    location_data, answer = handler.get_response(test_question)
    
    print("\nResults:")
    print(f"Location data: {location_data}")
    print(f"Answer: {answer}")


if __name__ == "__main__":
    test()
