# Post-Flight Telemetry Data Analysis Guide

Use the included diagnostic tools to inspect flight data:

1. Replay flight log in terminal:
   ```bash
   python tools/log_player.py logs/flight_sample.csv
   ```
2. Convert trajectory to Google Earth:
   ```bash
   python tools/csv_to_kml.py logs/flight_sample.csv flight.kml
   ```
3. Check communication health:
   ```bash
   python tools/link_health_check.py
   ```
