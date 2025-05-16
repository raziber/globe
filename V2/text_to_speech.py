import os
import tempfile
from pathlib import Path
import pygame
from openai import OpenAI

class TextToSpeech:
    def __init__(self, api_key=None):
        """
        Initialize the Text-to-Speech module using OpenAI's API.
        
        Args:
            api_key (str, optional): OpenAI API key. If not provided, it will look for OPENAI_API_KEY env variable.
        """
        # Use provided API key or get from environment
        if api_key is None:
            api_key = os.environ.get("OPENAI_API_KEY")
            if api_key is None:
                raise ValueError(
                    "OpenAI API key not found. Please provide an API key or set the OPENAI_API_KEY environment variable."
                )
        
        self.client = OpenAI(api_key=api_key)
        self.model = "tts-1"  # Default model
        self.voice = "alloy"   # Default voice
        
        # Initialize pygame mixer for audio playback
        pygame.mixer.init()
        
        # Create a directory for temporary audio files if it doesn't exist
        self.audio_dir = Path(tempfile.gettempdir()) / "globe_assistant_audio"
        self.audio_dir.mkdir(exist_ok=True)
        
        print("Text-to-speech module initialized.")
    
    def set_voice(self, voice):
        """
        Set the voice to use for TTS.
        
        Args:
            voice (str): One of the available OpenAI voices: 
                         'alloy', 'echo', 'fable', 'onyx', 'nova', or 'shimmer'
        """
        available_voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        if voice not in available_voices:
            raise ValueError(f"Voice '{voice}' not available. Choose from: {', '.join(available_voices)}")
        
        self.voice = voice
        print(f"Voice set to: {self.voice}")
    
    def set_model(self, model):
        """
        Set the model to use for TTS.
        
        Args:
            model (str): One of the available TTS models: 'tts-1' or 'tts-1-hd'
        """
        available_models = ["tts-1", "tts-1-hd"]
        if model not in available_models:
            raise ValueError(f"Model '{model}' not available. Choose from: {', '.join(available_models)}")
            
        self.model = model
        print(f"Model set to: {self.model}")
    
    def generate_speech(self, text):
        """
        Generate speech from text using OpenAI's TTS API.
        
        Args:
            text (str): The text to convert to speech
            
        Returns:
            Path: Path to the generated audio file
        """
        try:
            # Generate a temporary file path
            output_file = self.audio_dir / f"globe_tts_{id(text)}.mp3"
            
            # Request speech generation from OpenAI
            print(f"Generating speech using {self.model} with voice {self.voice}...")
            response = self.client.audio.speech.create(
                model=self.model,
                voice=self.voice,
                input=text
            )
            
            # Save the audio file
            response.stream_to_file(output_file)
            print(f"Speech generated and saved to {output_file}")
            
            return output_file
            
        except Exception as e:
            print(f"Error generating speech: {e}")
            return None
    
    def speak(self, text):
        """
        Convert text to speech and play it.
        
        Args:
            text (str): The text to speak
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Generate speech
            audio_file = self.generate_speech(text)
            if audio_file is None:
                return False
                
            # Play the audio
            print("Playing audio...")
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            
            # Wait for the audio to finish playing
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
                
            return True
            
        except Exception as e:
            print(f"Error during speech playback: {e}")
            return False
    
    def cleanup(self):
        """
        Clean up temporary audio files and resources.
        """
        try:
            # Stop any playing audio
            pygame.mixer.music.stop()
            
            # Clean up temp files that are older than 1 hour
            import time
            current_time = time.time()
            for file in self.audio_dir.glob("globe_tts_*.mp3"):
                if current_time - file.stat().st_mtime > 3600:  # 1 hour in seconds
                    try:
                        file.unlink()
                    except Exception as e:
                        print(f"Could not delete temporary file {file}: {e}")
                        
            print("Text-to-speech cleanup complete.")
            
        except Exception as e:
            print(f"Error during cleanup: {e}")


# Test function to verify functionality
def test():
    # First check if API key is set
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("WARNING: OPENAI_API_KEY environment variable not set. Testing will fail.")
        print("Please set your OpenAI API key with:")
        print('$env:OPENAI_API_KEY = "your-api-key"')
        return

    try:
        tts = TextToSpeech()
        test_text = "Hello! I'm your Smart Globe Assistant. How can I help you today?"
        
        print(f"Testing text-to-speech with: '{test_text}'")
        success = tts.speak(test_text)
        
        if success:
            print("\nSuccessfully generated and played speech!")
        else:
            print("\nFailed to generate or play speech.")
            
        # Test different voices
        voices = ["alloy", "echo", "nova", "shimmer"]
        for voice in voices:
            response = input(f"\nWould you like to hear the '{voice}' voice? (y/n): ")
            if response.lower() == 'y':
                tts.set_voice(voice)
                tts.speak(f"This is the {voice} voice. I hope you like it!")
        
        tts.cleanup()
        
    except Exception as e:
        print(f"Error during TTS test: {e}")


if __name__ == "__main__":
    test()
