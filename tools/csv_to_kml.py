"""Converts recorded CSV flight coordinates into Google Earth KML format."""

import csv
import sys

def convert_csv_to_kml(csv_path: str, kml_path: str):
    coords = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            coords.append(f"{row['lon']},{row['lat']},{row['alt_rel']}")

    coord_str = " ".join(coords)
    kml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>KKRTI Flight Trajectory</name>
    <Placemark>
      <LineString>
        <coordinates>{coord_str}</coordinates>
      </LineString>
    </Placemark>
  </Document>
</kml>"""
    with open(kml_path, "w", encoding="utf-8") as f:
        f.write(kml_content)
    print(f"KML generated successfully at {kml_path}")

if __name__ == "__main__":
    if len(sys.argv) > 2:
        convert_csv_to_kml(sys.argv[1], sys.argv[2])
    else:
        print("Usage: python csv_to_kml.py <input.csv> <output.kml>")
