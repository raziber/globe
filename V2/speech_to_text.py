import speech_recognition as sr

class SpeechToText:
    def __init__(self):
        """Initialize the speech recognition components."""
        self.recognizer = sr.Recognizer()
        
        # Adjust for ambient noise level and microphone sensitivity
        self.energy_threshold = 4000  # Default: 300
        self.recognizer.energy_threshold = self.energy_threshold
        
        # How long to wait in non-speaking audio before considering the phrase complete
        self.pause_threshold = 0.8  # Default: 0.8
        self.recognizer.pause_threshold = self.pause_threshold
        
        # Initialize microphone
        self.microphone = sr.Microphone()
        print("Speech to text module initialized.")
    
    def calibrate_for_ambient_noise(self, duration=1):
        """Calibrate the recognizer for ambient noise levels."""
        print("Calibrating for ambient noise... Please be quiet.")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=duration)
        print(f"Calibration complete. Energy threshold set to {self.recognizer.energy_threshold}")
        self.energy_threshold = self.recognizer.energy_threshold
    
    def listen_for_wake_word(self, wake_words=None):
        """
        Listen for a specific wake word.
        
        Args:
            wake_words (list): List of wake words to listen for. Default is ["hey globe", "hey assistant"]
            
        Returns:
            bool: True if wake word is detected, False if error occurs
        """
        if wake_words is None:
            wake_words = ["hey globe", "hey assistant"]
        
        wake_words = [word.lower() for word in wake_words]
        
        try:
            print("Listening for wake word...")
            with self.microphone as source:
                audio = self.recognizer.listen(source)
                
            try:
                text = self.recognizer.recognize_google(audio).lower()
                print(f"Heard: {text}")
                
                for wake_word in wake_words:
                    if wake_word in text:
                        print(f"Wake word '{wake_word}' detected!")
                        return True
                
                # Wake word not detected
                return False
            
            except sr.UnknownValueError:
                # Speech was unintelligible
                return False
            
            except sr.RequestError as e:
                print(f"Could not request results: {e}")
                return False
                
        except Exception as e:
            print(f"Error in wake word detection: {e}")
            return False
    
    def listen_for_query(self, timeout=None, phrase_time_limit=None):
        """
        Listen for and transcribe user speech.
        
        Args:
            timeout (int, optional): How long to wait for speech before giving up
            phrase_time_limit (int, optional): Maximum length of a phrase
            
        Returns:
            str: Transcribed text, or empty string if error
        """
        try:
            print("Listening for your question...")
            with self.microphone as source:
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )
                
            try:
                text = self.recognizer.recognize_google(audio)
                print(f"Recognized: {text}")
                return text
                
            except sr.UnknownValueError:
                print("Could not understand audio")
                return ""
                
            except sr.RequestError as e:
                print(f"Could not request results: {e}")
                return ""
                
        except Exception as e:
            print(f"Error in speech recognition: {e}")
            return ""


# Simple test function to verify functionality
def test():
    stt = SpeechToText()
    stt.calibrate_for_ambient_noise(duration=2)
    
    print("Testing wake word detection...")
    while not stt.listen_for_wake_word():
        pass
    
    print("Wake word detected! Now listening for your query...")
    query = stt.listen_for_query(phrase_time_limit=5)
    print(f"Your query was: '{query}'")


if __name__ == "__main__":
    test()
