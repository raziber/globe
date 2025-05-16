"""
Simple test script to test the text-to-speech functionality.
This script lets you test different voices and text samples with OpenAI's TTS-1 model.
"""
import os
from text_to_speech import TextToSpeech

def check_api_key():
    """Check if the OpenAI API key is set."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("\n\033[91mError: OpenAI API key not found!\033[0m")
        print("Please set your OpenAI API key as an environment variable.")
        print("For PowerShell:")
        print('  $env:OPENAI_API_KEY = "your-api-key-here"')
        print("For Command Prompt:")
        print('  set OPENAI_API_KEY=your-api-key-here')
        return False
    return True

def test_tts():
    """Test the text-to-speech functionality."""
    if not check_api_key():
        return
    
    print("Testing Text-to-Speech functionality...")
    
    try:
        tts = TextToSpeech()
        
        # Test different voices
        voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        
        # Intro message
        print("\nWelcome to the TTS Voice Test!")
        print("You'll hear samples of different OpenAI TTS voices.")
        print("For each voice, you can enter custom text to hear or press Enter to use the default text.")
        
        # Default test message
        default_text = "Hello, I'm your Smart Globe Assistant. I can help you explore the world."
        
        for voice in voices:
            print(f"\n\033[94mTesting voice: {voice}\033[0m")
            tts.set_voice(voice)
            
            custom_text = input(f"Enter text to speak with {voice} voice (or press Enter for default): ")
            text_to_speak = custom_text if custom_text else default_text
            
            print(f"Speaking with {voice} voice: '{text_to_speak}'")
            tts.speak(text_to_speak)
            
            # Ask if the user wants to continue
            if voice != voices[-1]:  # If not the last voice
                response = input("\nPress Enter to continue to next voice, or 'q' to quit: ")
                if response.lower() == 'q':
                    break
        
        # Test HD model
        response = input("\nWould you like to test the high-definition model (tts-1-hd)? (y/n): ")
        if response.lower() == 'y':
            try:
                print("\n\033[94mTesting HD model with Nova voice\033[0m")
                tts.set_model("tts-1-hd")
                tts.set_voice("nova")
                custom_text = input("Enter text for HD voice (or press Enter for default): ")
                text_to_speak = custom_text if custom_text else "This is the high-definition model. Notice the improved audio quality and natural speech patterns."
                print(f"Speaking with HD model: '{text_to_speak}'")
                tts.speak(text_to_speak)
            except Exception as e:
                print(f"\033[91mError testing HD model: {e}\033[0m")
        
        # Clean up
        tts.cleanup()
        print("\n\033[92mText-to-speech test completed successfully!\033[0m")
        
    except Exception as e:
        print(f"\n\033[91mError during TTS test: {e}\033[0m")

if __name__ == "__main__":
    test_tts()
