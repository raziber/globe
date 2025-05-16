import json
import time
import socket
import threading
from typing import List, Optional

# Constants
DEFAULT_SERVER_IP = '100.85.4.50'
DEFAULT_SERVER_PORT = 5000
DEFAULT_MIN_DELAY = 0.2  # Seconds
TOTAL_LEDS = 402
SOCKET_TIMEOUT = 5.0  # Socket timeout in seconds
RECONNECT_DELAY_INITIAL = 2.0  # Initial delay before reconnecting
RECONNECT_DELAY_MAX = 30.0  # Maximum delay before reconnecting
RECONNECT_BACKOFF_FACTOR = 1.5  # Factor to increase delay by on each attempt
SOCKET_BUFFER_SIZE = 2048  # Buffer size for receiving data
CONNECTION_RETRY_COUNT = 5  # Number of retries for connection

class SocketClient:
    """
    Socket client to send LED data to the globe.
    
    Sends RGB values for TOTAL_LEDS LEDs to a specified IP address with 
    a minimum delay between sends to prevent overwhelming the server.
    """
    
    def __init__(self, ip: str = DEFAULT_SERVER_IP, port: int = DEFAULT_SERVER_PORT, 
                 min_delay: float = DEFAULT_MIN_DELAY):
        """
        Initialize the socket client.
        
        Args:
            ip (str): IP address of the server
            port (int): Port number of the server
            min_delay (float): Minimum delay between sends in seconds
        """
        self.server_ip = ip
        self.server_port = port
        self.min_delay = min_delay
        self.last_send_time = 0
        self.connection = None
        self.is_connected = False
        self.lock = threading.Lock()
        self.socket_thread = None
        self.pending_data = None
        self.stop_event = threading.Event()
        
        print(f"Socket client initialized with server {self.server_ip}:{self.server_port}")

    def start(self):
        """
        Start the socket client in a separate thread.
        """
        if self.socket_thread is not None and self.socket_thread.is_alive():
            print("Socket client is already running")
            return
        
        self.stop_event.clear()
        self.socket_thread = threading.Thread(target=self._connection_loop)
        self.socket_thread.daemon = True
        self.socket_thread.start()
        print("Socket client started")

    def stop(self):
        """
        Stop the socket client.
        """
        if self.socket_thread is None or not self.socket_thread.is_alive():
            print("Socket client is not running")
            return
        
        print("Stopping socket client...")
        self.stop_event.set()
        
        # Close the connection
        self._close_connection()
        
        self.socket_thread.join(timeout=5)
        if self.socket_thread.is_alive():
            print("Warning: Socket thread did not terminate properly")
        else:
            print("Socket client stopped")
            
    def _connection_loop(self):
        """
        Main connection loop that tries to maintain a connection and process data.
        """
        retry_interval = RECONNECT_DELAY_INITIAL
        
        while not self.stop_event.is_set():
            try:
                # Create a new socket
                self._connect_to_server()
                
                if self.is_connected:
                    # Reset retry interval on successful connection
                    retry_interval = RECONNECT_DELAY_INITIAL
                    
                    # Process pending data
                    while not self.stop_event.is_set() and self.is_connected:
                        # Check for pending data
                        data_to_send = None
                        with self.lock:
                            if self.pending_data is not None:
                                data_to_send = self.pending_data
                                self.pending_data = None
                        
                        if data_to_send is not None:
                            try:
                                self._send_data(data_to_send)
                            except Exception as e:
                                print(f"Error sending data: {e}")
                                self.is_connected = False
                                break  # Break the inner loop to reconnect
                        
                        # Small delay to prevent CPU hogging
                        time.sleep(0.01)
            
            except Exception as e:
                print(f"Socket error: {e}")
            
            # Only attempt to reconnect if we're not stopping
            if not self.stop_event.is_set():
                print(f"Reconnecting in {retry_interval} seconds...")
                # Wait for the retry interval or until stop is requested
                start_wait = time.time()
                while time.time() - start_wait < retry_interval:
                    if self.stop_event.is_set():
                        break
                    time.sleep(0.1)
                    
                # Exponential backoff with max
                retry_interval = min(retry_interval * RECONNECT_BACKOFF_FACTOR, RECONNECT_DELAY_MAX)
            
            self._close_connection()

    def _connect_to_server(self):
        """
        Connect to the server.
        
        Returns:
            bool: True if connection was successful, False otherwise
        """
        print(f"Connecting to {self.server_ip}:{self.server_port}...")
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.settimeout(SOCKET_TIMEOUT)
        
        # Try to connect with retries
        for attempt in range(CONNECTION_RETRY_COUNT):
            try:
                self.connection.connect((self.server_ip, self.server_port))
                self.is_connected = True
                print(f"Connected to server at {self.server_ip}:{self.server_port}")
                return True
            except (socket.timeout, ConnectionRefusedError) as e:
                if attempt < CONNECTION_RETRY_COUNT - 1:
                    print(f"Connection attempt {attempt+1} failed: {e}. Retrying...")
                    time.sleep(1)
                else:
                    print(f"Connection failed after {CONNECTION_RETRY_COUNT} attempts: {e}")
                    self._close_connection()
                    return False
            except Exception as e:
                print(f"Unexpected error while connecting: {e}")
                self._close_connection()
                return False
        
        return False

    def _close_connection(self):
        """
        Close the socket connection.
        """
        self.is_connected = False
        if self.connection:
            try:
                self.connection.close()
            except Exception as e:
                print(f"Error closing connection: {e}")
        self.connection = None

    def _send_data(self, led_data: List[List[int]]):
        """
        Send LED data over socket with rate limiting.
        
        Args:
            led_data: List of RGB values for each LED
        """
        if not self.is_connected or not self.connection:
            print("Not connected, cannot send data")
            return
            
        current_time = time.time()
        time_since_last_send = current_time - self.last_send_time
        
        # Apply rate limiting
        if time_since_last_send < self.min_delay:
            time.sleep(self.min_delay - time_since_last_send)
            
        # Send the data with a newline at the end for line-based processing
        json_data = json.dumps(led_data) + '\n'
        try:
            self.connection.sendall(json_data.encode('utf-8'))
            self.last_send_time = time.time()
        except Exception as e:
            print(f"Error sending data: {e}")
            self.is_connected = False
            raise
        
    def send_led_data(self, led_data: List[List[int]]):
        """
        Queue LED data to be sent over socket.
        If another send is already pending, replaces it with this new data.
        
        Args:
            led_data: List of TOTAL_LEDS RGB values for the LEDs
            
        Returns:
            bool: True if the data was queued, False if invalid or client not started
        """
        if not self.socket_thread or not self.socket_thread.is_alive():
            print("Socket client is not running, call start() first")
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
            print(f"Error: Expected {TOTAL_LEDS} LEDs but got {len(led_data)}")
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
def test_socket_client():
    """Test the socket client with a sample pattern."""
    client = SocketClient()
    client.start()
    
    try:
        # Create a sample LED data array (all red)
        led_data = [[255, 0, 0] for _ in range(TOTAL_LEDS)]
        
        # Send the data
        print("Sending all red")
        client.send_led_data(led_data)
        
        # Wait a bit
        time.sleep(2)
        
        # Create another pattern (all blue)
        led_data = [[0, 0, 255] for _ in range(TOTAL_LEDS)]
        
        # Send the new data
        print("Sending all blue")
        client.send_led_data(led_data)
        
        # Wait for it to be sent
        time.sleep(2)
        
        # Create a rainbow pattern
        print("Sending rainbow pattern")
        rainbow_data = []
        for i in range(TOTAL_LEDS):
            # Create a rainbow-like effect
            hue = (i / TOTAL_LEDS) * 360
            if hue < 60:
                r, g, b = 255, int((hue / 60) * 255), 0
            elif hue < 120:
                r, g, b = int(((120 - hue) / 60) * 255), 255, 0
            elif hue < 180:
                r, g, b = 0, 255, int(((hue - 120) / 60) * 255)
            elif hue < 240:
                r, g, b = 0, int(((240 - hue) / 60) * 255), 255
            elif hue < 300:
                r, g, b = int(((hue - 240) / 60) * 255), 0, 255
            else:
                r, g, b = 255, 0, int(((360 - hue) / 60) * 255)
            rainbow_data.append([r, g, b])
        
        client.send_led_data(rainbow_data)
        time.sleep(2)
        
        # Turn off all LEDs
        print("Turning off all LEDs")
        off_data = [[0, 0, 0] for _ in range(TOTAL_LEDS)]
        client.send_led_data(off_data)
        time.sleep(1)
        
    finally:
        # Always stop the client when done
        client.stop()


if __name__ == "__main__":
    print("Testing Socket client...")
    test_socket_client()
