# KML Point to DJI Mission Waypoint Converter

**Author:** Kenneth Dale ([ken@insightdrone.ca](mailto:ken@insightdrone.ca))

This script converts KML files containing multiple points into DJI mission-compatible waypoint KML files. Each output file contains a mission that starts at a base point and flies to a destination point.

## Directory Structure

```
kmls-to-multi/
├── convert.py              # Main conversion script
├── base_kml/               # Contains base.kml with the starting point
├── input_points_kml/       # Contains KML files with destination points (can have multiple points per file)
└── output_paths/           # Generated DJI mission KML files will be saved here
```

## Setup

1. Make sure you have Python 3.7+ installed
2. Install required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

   Or install manually:

   ```bash
   pip install simplekml lxml
   ```

## Usage

### 1. Prepare Input Files

**Base Point:**

- Create a file named `base.kml` in the `base_kml/` directory
- This file should contain a single point that will serve as the starting location for all missions

**Destination Points:**

- Place KML files with destination points in the `input_points_kml/` directory
- Each KML file can contain multiple points (each will generate a separate mission)
- Points can include HTML table data in their descriptions for enhanced naming
- The script will extract location names from HTML tables in the KML descriptions

### 2. Run the Script

```bash
python convert.py
```

### 3. Output

The script will generate DJI mission KML files in the `output_paths/` directory. Each output file will:

- Be named with a 3-digit number and extracted location name (e.g., `001_Info_Center.kml`, `025_6__Shambhalodging_Main.kml`)
- Contain a LineString path from the base point to the destination point
- Use the exact format required by DJI mission planning software
- Include proper styling and tessellation for optimal DJI compatibility

## KML File Format

### Input KML Format

Your input KML files should follow this structure:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Location Points</name>
    <Placemark>
      <name>Location Name</name>
      <description><![CDATA[
        <html>
          <body>
            <table>
              <tr style="background:#9CBCE2">
                <td>Location Identifier</td>
              </tr>
              <!-- Additional table data -->
            </table>
          </body>
        </html>
      ]]></description>
      <Point>
        <coordinates>longitude,latitude,altitude</coordinates>
      </Point>
    </Placemark>
  </Document>
</kml>
```

### Output Features

Each generated mission KML includes:

- **LineString path**: Direct flight path from base to destination point
- **DJI-compatible format**: Uses the exact XML structure required by DJI software
- **Proper styling**: Includes StyleMap and icon definitions for visualization
- **Tessellation**: Enables smooth path rendering in DJI applications

## Example

If you have:

- `base_kml/base.kml` (base point at coordinates -117.2738922672704,49.10373549840682,0)
- `input_points_kml/SMF_Points.kml` (containing multiple destination points with HTML table data)

The script will generate:

- `output_paths/001_Info_Center.kml` (mission from base to Info Center)
- `output_paths/002_27__Grove_South.kml` (mission from base to Grove South)
- `output_paths/025_6__Shambhalodging_Main.kml` (mission from base to Shambhalodging Main)
- And 49 more mission files for each destination point found

## Features

- **Automatic HTML parsing**: Extracts location identifiers from HTML tables in KML descriptions
- **Sequential numbering**: Files are numbered 001, 002, 003, etc. for easy organization
- **DJI compatibility**: Generates KML files in the exact format required by DJI mission planning software
- **Batch processing**: Handles multiple destination points from a single input file
- **Clean filename generation**: Removes special characters and formats names for filesystem compatibility

## Troubleshooting

- **"Base KML file not found"**: Make sure `base.kml` exists in the `base_kml/` directory
- **"No destination points found"**: Verify that your KML files are in the `input_points_kml/` directory and contain valid point coordinates
- **"Could not extract coordinates"**: Check that your KML files contain properly formatted `<coordinates>` elements
- **"Could not extract HTML table attribute"**: The script looks for HTML tables in KML descriptions - if none are found, files will still be generated but without extracted names

## Technical Details

- **HTML Table Parsing**: Uses regex to extract the first cell content from HTML tables with background colors
- **Coordinate Processing**: Handles longitude, latitude, and altitude from KML coordinate strings
- **File Naming**: Combines sequential numbers with cleaned HTML table attributes
- **DJI Format**: Generates LineString elements with tessellation for optimal DJI compatibility

## Coordinate Format

Coordinates should be in the format: `longitude,latitude,altitude`

- Longitude: East-West position (negative for West)
- Latitude: North-South position (negative for South)
- Altitude: Height in meters (optional, defaults to 0)
