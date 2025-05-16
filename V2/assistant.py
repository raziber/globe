from enum import Enum
import os
from speech_to_text import SpeechToText
from gpt_handler import GPTHandler
from text_to_speech import TextToSpeech
import time

class State(Enum):
    IDLE = 1
    LISTENING = 2 
    PROCESSING = 3
    RESPONDING = 4

class Assistant:
    def __init__(self):
        self.state = State.IDLE
        self.speech_to_text = SpeechToText()
        # Calibrate microphone for ambient noise
        self.speech_to_text.calibrate_for_ambient_noise(duration=1)
        
        # Initialize the GPT handler
        try:
            self.gpt_handler = GPTHandler()
            self.gpt_available = True
        except ValueError as e:
            print(f"Warning: {e}")
            print("GPT functionality will not be available.")
            self.gpt_available = False
            
        # Initialize the text-to-speech handler
        try:
            self.text_to_speech = TextToSpeech()
            self.tts_available = True
            # Select a voice - you can change this to any of:
            # "alloy", "echo", "fable", "onyx", "nova", "shimmer"
            self.text_to_speech.set_voice("nova")  # A pleasant, clear voice
        except ValueError as e:
            print(f"Warning: {e}")
            print("Text-to-speech functionality will not be available.")
            self.tts_available = False
            
        print("Assistant initialized.")

    def run(self):
        while True:
            if self.state == State.IDLE:
                self.handle_idle_state()
            elif self.state == State.LISTENING:
                self.handle_listening_state()
            elif self.state == State.PROCESSING:
                self.handle_processing_state()
            elif self.state == State.RESPONDING:
                self.handle_responding_state()

    def handle_idle_state(self):
        """
        In idle state, the assistant is waiting for a wake word.
        Once the wake word is detected, transition to LISTENING state.
        """
        print("State: IDLE - Waiting for wake word...")
        wake_words = ["hey globe", "hey assistant", "ok globe", "smart globe"]
        
        # Try to detect wake word, if an exception occurs or wake word isn't detected,
        # we'll stay in the idle state
        if self.speech_to_text.listen_for_wake_word(wake_words=wake_words):
            self.state = State.LISTENING

    def handle_listening_state(self):
        """
        In listening state, the assistant is waiting for the user's question.
        Once the question is received, transition to PROCESSING state.
        """
        print("State: LISTENING - Waiting for your question...")
        
        # Use speech-to-text to capture user's question
        # Using a phrase time limit of 7 seconds for query length
        query = self.speech_to_text.listen_for_query(phrase_time_limit=7)
        
        # If speech recognition fails or returns empty string,
        # let's fall back to text input
        if not query:
            print("Voice input not recognized, please type your question.")
            query = input("You: ")
            
        if query.lower() == "exit":
            print("Exiting...")
            exit(0)
            
        self.current_query = query
        self.state = State.PROCESSING

    def handle_processing_state(self):
        """
        In processing state, the assistant processes the user's question.
        Once processing is complete, transition to RESPONDING state.
        """
        print(f"State: PROCESSING - Processing your question: '{self.current_query}'")
        
        # Get response from OpenAI if available, otherwise use fallback
        if self.gpt_available:
            try:
                # Get weather data here if available
                weather_summary = None  # You can implement weather API integration here
                
                # Get response from GPT
                print("Sending request to OpenAI...")
                location_data, answer_text = self.gpt_handler.get_response(
                    self.current_query, 
                    weather_summary
                )
                
                # Store both location data and text response
                self.location_data = location_data
                self.response = answer_text
                
                # For debugging, print location data if available
                if location_data:
                    print(f"Location data: {location_data}")
                    
            except Exception as e:
                print(f"Error processing with GPT: {e}")
                self.response = f"I'm sorry, I encountered an error processing your request: {str(e)}"
                self.location_data = None
        else:            # Fallback if GPT is not available
            print("GPT not available, using fallback response")
            self.response = f"You asked: '{self.current_query}'. I'm sorry, but I can't provide a detailed answer right now."
            self.location_data = None
            
        self.state = State.RESPONDING
        
    def handle_responding_state(self):
        """
        In responding state, the assistant responds to the user's question.
        Once the response is delivered, transition back to IDLE state.
        """
        print(f"State: RESPONDING - Responding to your question")
        
        # Display the response
        print(f"Globe Assistant: {self.response}")
        
        # Use text-to-speech if available
        if self.tts_available:
            try:
                print("Speaking response...")
                self.text_to_speech.speak(self.response)
            except Exception as e:
                print(f"Error in text-to-speech: {e}")
        
        # If there's location data, you would update the globe visualization
        if hasattr(self, 'location_data') and self.location_data:
            location_type = self.location_data.get('type')
            if location_type == 'point':
                lat = self.location_data.get('lat')
                lon = self.location_data.get('lon')
                color = self.location_data.get('color_rgb', [255, 0, 0])  # Default to red if no color specified
                print(f"Globe should highlight point: Latitude {lat}, Longitude {lon} with color {color}")
                # Here you would call your globe visualization function
                # For example: globe.highlight_point(lat, lon, color)
                
            elif location_type == 'region':
                polygon = self.location_data.get('polygon', [])
                color = self.location_data.get('color_rgb', [0, 0, 255])  # Default to blue if no color specified
                print(f"Globe should highlight region with {len(polygon)} points and color {color}")                # Here you would call your globe visualization function
                # For example: globe.highlight_region(polygon, color)
        
        import time
        time.sleep(1)  # Pause before returning to idle
        self.state = State.IDLE
        
    def cleanup(self):
        """
        Clean up resources before exiting.
        """
        print("Cleaning up Assistant resources...")
        
        # Clean up text-to-speech resources if available
        if hasattr(self, 'tts_available') and self.tts_available:
            try:
                print("Cleaning up text-to-speech resources...")
                self.text_to_speech.cleanup()
            except Exception as e:
                print(f"Error cleaning up text-to-speech: {e}")
                
        print("Assistant cleanup complete.")
