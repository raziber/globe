import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from assistant import Assistant

def setup_environment():
    """Load environment variables from .env file if it exists."""
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print("Loaded environment variables from .env file")
    
    # Check for required API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("\nWARNING: No OpenAI API key found!")
        print("The assistant will run in limited mode without AI capabilities.")
        print("To enable AI features, set your OpenAI API key by either:")
        print("1. Creating a .env file with OPENAI_API_KEY=your-key-here, or")
        print("2. Setting the environment variable: $env:OPENAI_API_KEY = 'your-key-here'")
        
        # Prompt user if they want to continue
        response = input("\nDo you want to continue in limited mode? (y/n): ")
        if response.lower() != 'y':
            print("Exiting...")
            sys.exit(0)

def cleanup():
    """Clean up resources before exiting."""
    print("\nCleaning up resources...")
    # Add any necessary cleanup code here
    print("Cleanup complete.")

if __name__ == "__main__":
    print("Starting Smart Globe Assistant...")
    setup_environment()
    print("Press Ctrl+C to exit")

    try:
        assistant = Assistant()
        assistant.run()
    except KeyboardInterrupt:
        cleanup()
    except Exception as e:
        print(f"Error: {e}")
        cleanup()
        sys.exit(1)
