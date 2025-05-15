from smart_globe_assistant import SmartGlobeAssistant
import signal
import sys
from socket_connection import send_to_socket

def cleanup():
    """Clean up resources and reset LEDs before exit"""
    print("\n🛑 Smart Globe Assistant stopped")
    try:
        # Send empty data to reset LEDs
        send_to_socket({"type": "none"})
        print("✅ Reset LEDs to off state")
    except Exception as e:
        print(f"⚠️ Failed to reset LEDs: {e}")

def signal_handler(sig, frame):
    cleanup()
    sys.exit(0)

if __name__ == "__main__":
    # Register the signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    print("Starting Smart Globe Assistant...")
    print("Press Ctrl+C to exit")
    
    try:
        assistant = SmartGlobeAssistant("led_layout.json")
        assistant.run()
    except KeyboardInterrupt:
        cleanup()
