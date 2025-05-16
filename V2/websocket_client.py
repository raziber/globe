import asyncio
import json
import time
import websockets
import threading
from typing import List, Tuple, Optional

# Constants
DEFAULT_SERVER_IP = '100.85.4.50'
DEFAULT_SERVER_PORT = 5000
DEFAULT_MIN_DELAY = 0.2  # Seconds
TOTAL_LEDS = 402

class WebSocketClient:
    """
    WebSocket client to send LED data to the globe.
    
    Sends RGB values for TOTAL_LEDS LEDs to a specified IP address with 
    a minimum delay between sends to prevent overwhelming the server.
    """
    
    def __init__(self, ip: str = DEFAULT_SERVER_IP, port: int = DEFAULT_SERVER_PORT, min_delay: float = DEFAULT_MIN_DELAY):
        """
        Initialize the WebSocket client.
        
        Args:
            ip (str): IP address of the WebSocket server
            port (int): Port number of the WebSocket server
            min_delay (float): Minimum delay between sends in seconds
        """
        self.server_uri = f"ws://{ip}:{port}"
        self.min_delay = min_delay
        self.last_send_time = 0
        self.connection = None
        self.is_connected = False
        self.lock = threading.Lock()
        self.event_loop = None
        self.websocket_thread = None
        self.pending_data = None
        self.stop_event = threading.Event()
        
        print(f"WebSocket client initialized with server {self.server_uri}")

    def start(self):
        """
        Start the WebSocket client in a separate thread.
        """
        if self.websocket_thread is not None and self.websocket_thread.is_alive():
            print("WebSocket client is already running")
            return
        
        self.stop_event.clear()
        self.websocket_thread = threading.Thread(target=self._run_event_loop)
        self.websocket_thread.daemon = True
        self.websocket_thread.start()
        print("WebSocket client started")

    def stop(self):
        """
        Stop the WebSocket client.
        """
        if self.websocket_thread is None or not self.websocket_thread.is_alive():
            print("WebSocket client is not running")
            return
        
        print("Stopping WebSocket client...")
        self.stop_event.set()
        
        if self.event_loop and self.connection:
            asyncio.run_coroutine_threadsafe(self._close_connection(), self.event_loop)
        
        self.websocket_thread.join(timeout=5)
        if self.websocket_thread.is_alive():
            print("Warning: WebSocket thread did not terminate properly")
        else:
            print("WebSocket client stopped")

    def _run_event_loop(self):
        """
        Run the asyncio event loop in a separate thread.
        """
        self.event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.event_loop)
        try:
            self.event_loop.run_until_complete(self._connection_loop())
        except Exception as e:
            print(f"Error in WebSocket thread: {e}")
        finally:
            self.event_loop.close()
            self.event_loop = None
            print("WebSocket event loop closed")    
            
    async def _connection_loop(self):
        """
        Main connection loop that tries to maintain a connection and process data.
        """
        INITIAL_RETRY_INTERVAL = 2  # Seconds
        MAX_RETRY_INTERVAL = 30     # Seconds
        BACKOFF_MULTIPLIER = 1.5    # Exponential backoff factor
        
        retry_interval = INITIAL_RETRY_INTERVAL
        
        while not self.stop_event.is_set():
            try:
                print(f"Connecting to {self.server_uri}...")
                async with websockets.connect(self.server_uri) as websocket:
                    print("Connected to WebSocket server")
                    self.connection = websocket
                    self.is_connected = True
                    retry_interval = INITIAL_RETRY_INTERVAL  # Reset retry interval on successful connection
                    
                    while not self.stop_event.is_set():
                        # Check for pending data
                        data_to_send = None
                        with self.lock:
                            if self.pending_data is not None:
                                data_to_send = self.pending_data
                                self.pending_data = None
                        
                        if data_to_send is not None:
                            try:
                                await self._send_data(data_to_send)
                            except Exception as e:
                                print(f"Error sending data: {e}")
                                break  # Break the inner loop to reconnect
                        
                        # Small delay to prevent CPU hogging
                        await asyncio.sleep(0.01)
                        
            except (websockets.exceptions.ConnectionClosed, 
                    websockets.exceptions.WebSocketException,
                    ConnectionRefusedError) as e:
                print(f"Connection error: {e}")
            except Exception as e:
                print(f"Unexpected error: {e}")
            
            # Only attempt to reconnect if we're not stopping
            if not self.stop_event.is_set():
                print(f"Reconnecting in {retry_interval} seconds...")
                # Wait for the retry interval or until stop is requested
                for _ in range(int(retry_interval * 100)):
                    if self.stop_event.is_set():
                        break
                    await asyncio.sleep(0.01)
                    
                # Exponential backoff with max
                retry_interval = min(retry_interval * BACKOFF_MULTIPLIER, MAX_RETRY_INTERVAL)
            
            self.is_connected = False
            self.connection = None

    async def _close_connection(self):
        """
        Close the WebSocket connection.
        """
        self.is_connected = False
        if self.connection:
            try:
                await self.connection.close()
            except Exception as e:
                print(f"Error closing connection: {e}")
        self.connection = None

    async def _send_data(self, led_data: List[List[int]]):
        """
        Send LED data over WebSocket with rate limiting.
        
        Args:
            led_data: List of RGB values for each LED
        """
        current_time = time.time()
        time_since_last_send = current_time - self.last_send_time
        
        # Apply rate limiting
        if time_since_last_send < self.min_delay:
            await asyncio.sleep(self.min_delay - time_since_last_send)
            
        # Send the data
        json_data = json.dumps(led_data)
        await self.connection.send(json_data)
        self.last_send_time = time.time()
        
    def send_led_data(self, led_data: List[List[int]]):
        """
        Queue LED data to be sent over WebSocket.
        If another send is already pending, replaces it with this new data.
        
        Args:
            led_data: List of TOTAL_LEDS RGB values for the LEDs
            
        Returns:
            bool: True if the data was queued, False if invalid or client not started
        """
        if not self.websocket_thread or not self.websocket_thread.is_alive():
            print("WebSocket client is not running, call start() first")
            return False
            
        # Validate the data
        if not self._validate_led_data(led_data):
            return False
            
        # Queue the data for sending
        with self.lock:
            self.pending_data = led_data
            
        return True
        
    def _validate_led_data(self, led_data: List[List[int]]) -> bool:
        """
        Validate that the LED data is correctly formatted.
        
        Args:
            led_data: List of RGB values for each LED
            
        Returns:
            bool: True if the data is valid, False otherwise
        """
        if not isinstance(led_data, list):
            print("Error: LED data must be a list")
            return False
            
        if len(led_data) != TOTAL_LEDS:
            print(f"Error: Expected TOTAL_LEDS LEDs but got {len(led_data)}")
            return False
            
        for i, rgb in enumerate(led_data):
            if not isinstance(rgb, list) or len(rgb) != 3:
                print(f"Error: LED {i} must be a list of 3 RGB values")
                return False
                
            for j, value in enumerate(rgb):
                if not isinstance(value, int) or value < 0 or value > 255:
                    print(f"Error: LED {i} color channel {j} must be an integer between 0 and 255")
                    return False
                    
        return True


# Example usage
def test_websocket_client():
    """Test the WebSocket client with a sample pattern."""
    client = WebSocketClient()
    client.start()
    
    try:
        # Create a sample LED data array (all red)
        led_data = [[255, 0, 0] for _ in range(TOTAL_LEDS)]
        
        # Send the data
        print("Sending all red")
        client.send_led_data(led_data)
        
        # Wait a bit
        time.sleep(1)
        
        # Create another pattern (all blue)
        led_data = [[0, 0, 255] for _ in range(TOTAL_LEDS)]
        
        # Send the new data
        print("Sending all blue")
        client.send_led_data(led_data)
        
        # Wait for it to be sent
        time.sleep(1)
        
    finally:
        # Always stop the client when done
        client.stop()


if __name__ == "__main__":
    print("Testing WebSocket client...")
    test_websocket_client()
