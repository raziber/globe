import sys

# ANSI escape sequences for color and bold
GREEN_BOLD = "\033[1;32m"
RED_BOLD = "\033[1;31m"
RESET = "\033[0m"

def decode_uart_frame(path):
    try:
        with open(path, "rb") as f:
            data = f.read()
    except FileNotFoundError:
        print(f"{RED_BOLD}❌ File not found: {path}{RESET}")
        return

    if len(data) < 4:
        print(f"{RED_BOLD}❌ Frame too short to contain a valid header.{RESET}")
        return

    # Parse header
    header = data[:2]
    length_bytes = data[2:4]
    stated_payload_length = int.from_bytes(length_bytes, byteorder='big')

    if header != b'\xAA\x55':
        print(f"{RED_BOLD}❌ Invalid header: expected AA 55{RESET}")
        return

    actual_payload = data[4:]
    actual_payload_length = len(actual_payload)

    full_led_count = actual_payload_length // 3
    has_extra_bytes = actual_payload_length % 3 != 0
    expected_led_count = stated_payload_length // 3
    led_count_matches = full_led_count == expected_led_count and not has_extra_bytes

    # Output details
    print(f"📦 Stated payload length in header: {stated_payload_length} bytes")
    print(f"📏 Actual payload length          : {actual_payload_length} bytes")
    print(f"💡 Number of full RGB LEDs       : {full_led_count}")
    print(f"✅ All LEDs have full RGB        : {'Yes' if not has_extra_bytes else 'No'}")
    print(f"🔁 LED count matches stated frame: {'Yes' if led_count_matches else 'No'}")

    # Final result
    if header == b'\xAA\x55' and not has_extra_bytes and led_count_matches:
        print(f"{GREEN_BOLD}✅ All checks passed. Frame is valid.{RESET}")
    else:
        print(f"{RED_BOLD}❌ Frame validation failed. See details above.{RESET}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 decode_uart.py <binary_file>")
    else:
        decode_uart_frame(sys.argv[1])

