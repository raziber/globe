import json

INPUT_FILE = "coordinates_shifted_1.json"
OUTPUT_FILE = "coordinates_shifted_2.json"

# Load original JSON
with open(INPUT_FILE, "r") as f:
    data = json.load(f)

# Shift IDs by 1
for entry in data:
    if entry["id"] >= 60:
      entry["id"] += 1

# Save to new file
with open(OUTPUT_FILE, "w") as f:
    json.dump(data, f, indent=2)

print(f"Shifted JSON saved to {OUTPUT_FILE}")
