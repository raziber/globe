# LED Globe Visualization Debug Report

## Problem Statement

The original issues with the LED globe visualization were:

1. Only half of the globe was turning blue at a time
2. LEDs 0-45 were sometimes being lit when they shouldn't be (first physical LED is LED 46)
3. No way to debug which LEDs were lighting up

## Solution Summary

### 1. Fixed half-globe update issue

- Modified `socket_client.py` to send each frame twice with a delay between sends
- This ensured complete data transmission to update the entire globe

### 2. Fixed incorrect LEDs lighting up

- Updated `_calculate_led_index` method to filter out LEDs with IDs less than 46
- Ensured correct mapping between geographic coordinates and LED positions

### 3. Created 3D visualization tools

- Implemented `globe_visualizer_3d.py` with comprehensive debugging capabilities:
  - 3D visualization of all LEDs on the globe
  - Highlighting specific points and regions
  - Visualizing LED IDs and their positions
  - Mapping between geographic coordinates and LED positions

## Using the Debug Tools

### Debug Script

The `debug_globe.py` script provides several visualization modes:

1. **All LEDs mode**

   ```
   python debug_globe.py --mode all
   ```

   Shows all LEDs on the globe in a 3D visualization.

2. **Point mode**

   ```
   python debug_globe.py --mode point --lat 40.7128 --lon -74.0060 --radius 5
   ```

   Visualizes which LEDs light up for a specific geographic point.

3. **Region mode**

   ```
   python debug_globe.py --mode region --polygon "51.5,-0.13;48.85,2.35;41.9,12.5;40.4,-3.7"
   ```

   Visualizes which LEDs light up for a polygon region.

4. **IDs mode**

   ```
   python debug_globe.py --mode ids --min_id 46
   ```

   Shows LED IDs on the globe, color-coded by ID value.

5. **Coverage mode**

   ```
   python debug_globe.py --mode coverage
   ```

   Shows how latitude and longitude map to LED IDs.

6. **Compare mode**
   ```
   python debug_globe.py --mode compare --lat 51.5074 --lon -0.1278
   ```
   Uses the globe's internal LED calculation and displays the results.

### Integration with GlobeVisualization

The `debug_leds` method was added to `GlobeVisualization` class:

```python
globe = GlobeVisualization()
globe.debug_leds({
    "type": "point",
    "lat": 51.5074,
    "lon": -0.1278
})
```

## Key Findings

1. **LED Distribution**

   - LEDs are distributed across the globe surface following spherical coordinates
   - Valid LED IDs start at 46 and go up to 402
   - Physical LED positions don't perfectly align with a regular grid

2. **ID vs. Position**

   - There is a clear relationship between LED ID and position (latitude/longitude)
   - Higher IDs generally correspond to higher latitudes
   - The coverage visualization shows exactly how IDs map to coordinates

3. **Debugging Process**
   - The 3D visualization makes it much easier to see which LEDs are lighting up
   - Point highlighting shows the LEDs surrounding a specific point
   - Region visualization shows how polygons are mapped to LEDs

## Conclusion

The combination of code fixes and new visualization tools has resolved both the half-globe update issue and the problem with incorrect LEDs lighting up. The 3D visualizer provides a powerful way to debug LED mappings and understand how geographic coordinates relate to the physical LEDs on the globe.
