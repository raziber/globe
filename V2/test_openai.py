"""
Simple test script to verify that the OpenAI integration works correctly.
This script will send a test query to OpenAI and display the response.
"""
import os
from gpt_handler import GPTHandler

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

def test_openai_integration():
    """Test the OpenAI integration by sending a test query."""
    if not check_api_key():
        return
    
    print("Testing OpenAI integration...")
    
    try:
        handler = GPTHandler()
        test_questions = [
            "Tell me about Paris, France",
            "Where is Mount Everest located?",
            "What's the capital of Australia?"
        ]
        
        for question in test_questions:
            print(f"\n\033[94mTesting with question: {question}\033[0m")
            
            location_data, answer = handler.get_response(question)
            
            print("\nResults:")
            if location_data:
                print(f"\033[92mLocation data: {location_data}\033[0m")
            else:
                print("\033[93mNo location data returned\033[0m")
                
            print(f"\033[92mAnswer: {answer}\033[0m")
            
            proceed = input("\nPress Enter to continue to next test, or 'q' to quit: ")
            if proceed.lower() == 'q':
                break
                
        print("\n\033[92mOpenAI integration test completed.\033[0m")
                
    except Exception as e:
        print(f"\n\033[91mError during OpenAI test: {e}\033[0m")

if __name__ == "__main__":
    test_openai_integration()
