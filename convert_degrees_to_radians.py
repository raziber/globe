import json
import math

def deg_to_rad_layout(input_file, output_file=None):
    with open(input_file, "r") as f:
        data = json.load(f)

    if not isinstance(data, list):
        print("❌ Expected a list of LED objects.")
        return

    for led in data:
        if "theta" in led and "phi" in led:
            # Convert from degrees to radians
            led["theta"] = math.radians(led["theta"])
            led["phi"] = math.radians(led["phi"])

    out_file = output_file or input_file
    with open(out_file, "w") as f:
        json.dump(data, f, indent=2)
    print(f"✅ Converted {len(data)} LEDs to radians and saved to {out_file}")

# Example usage
deg_to_rad_layout("coordinates_shifted_2.json", "led_layout.json")
