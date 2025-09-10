#!/usr/bin/env python3
"""
KML Point to DJI Mission Waypoint Converter

Author: Kenneth Dale (ken@insightdrone.ca)

This script reads KML files containing single points and creates DJI mission-compatible
waypoint KML files that define paths from a base point to each target point.

Input:
- base.kml: Contains the base/starting point (in input_point_kml/)
- Multiple KML files with single points each (in input_points_kmls/)

Output:
- Waypoint KML files for DJI missions (in output_paths/)
"""

import os
import sys
import xml.etree.ElementTree as ET
import simplekml
import re
from pathlib import Path


class KMLPointProcessor:
    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)
        self.base_kml_dir = self.base_dir / "base_kml"
        self.input_points_kml_dir = self.base_dir / "input_points_kml"
        self.output_paths_dir = self.base_dir / "output_paths"
        
        # Ensure output directory exists
        self.output_paths_dir.mkdir(exist_ok=True)
        
    def parse_kml_point(self, kml_file_path):
        """
        Parse a KML file and extract the first point coordinates.
        Returns (longitude, latitude, altitude) or None if no point found.
        """
        try:
            tree = ET.parse(kml_file_path)
            root = tree.getroot()
            
            # Handle KML namespace
            namespace = {'kml': 'http://www.opengis.net/kml/2.2'}
            
            # Find coordinates in the KML
            coordinates_elem = root.find('.//kml:coordinates', namespace)
            if coordinates_elem is None:
                # Try without namespace (some KML files don't use it)
                coordinates_elem = root.find('.//coordinates')
            
            if coordinates_elem is not None and coordinates_elem.text:
                # Parse coordinates (format: lon,lat,alt or lon,lat)
                coords_text = coordinates_elem.text.strip()
                coords = coords_text.split(',')
                
                if len(coords) >= 2:
                    lon = float(coords[0])
                    lat = float(coords[1])
                    alt = float(coords[2]) if len(coords) > 2 else 0.0
                    return (lon, lat, alt)
                    
        except Exception as e:
            print(f"Error parsing KML file {kml_file_path}: {e}")
            
        return None
    
    def parse_all_kml_points(self, kml_file_path):
        """
        Parse a KML file and extract all placemarks with their points and descriptions.
        Returns a list of dictionaries with point data.
        """
        points = []
        try:
            tree = ET.parse(kml_file_path)
            root = tree.getroot()
            
            # Handle KML namespace
            namespace = {'kml': 'http://www.opengis.net/kml/2.2'}
            
            # Find all placemarks
            placemarks = root.findall('.//kml:Placemark', namespace)
            if not placemarks:
                # Try without namespace
                placemarks = root.findall('.//Placemark')
            
            for i, placemark in enumerate(placemarks):
                # Get coordinates
                coordinates_elem = placemark.find('.//kml:coordinates', namespace)
                if coordinates_elem is None:
                    coordinates_elem = placemark.find('.//coordinates')
                
                if coordinates_elem is not None and coordinates_elem.text:
                    coords_text = coordinates_elem.text.strip()
                    coords = coords_text.split(',')
                    
                    if len(coords) >= 2:
                        lon = float(coords[0])
                        lat = float(coords[1])
                        alt = float(coords[2]) if len(coords) > 2 else 0.0
                        
                        # Get placemark name
                        name_elem = placemark.find('.//kml:name', namespace)
                        if name_elem is None:
                            name_elem = placemark.find('.//name')
                        name = name_elem.text if name_elem is not None and name_elem.text else f"Point_{i+1}"
                        
                        # Get description for HTML table extraction
                        desc_elem = placemark.find('.//kml:description', namespace)
                        if desc_elem is None:
                            desc_elem = placemark.find('.//description')
                        description = desc_elem.text if desc_elem is not None and desc_elem.text else ""
                        
                        # Extract table attribute from description
                        table_attribute = self.extract_html_table_attribute_from_text(description)
                        
                        points.append({
                            'name': name,
                            'coordinates': (lon, lat, alt),
                            'description': description,
                            'table_attribute': table_attribute
                        })
                        
        except Exception as e:
            print(f"Error parsing KML file {kml_file_path}: {e}")
            
        return points
    
    def extract_html_table_attribute_from_text(self, html_text):
        """
        Extract the first cell content from the first HTML table in the given text.
        Returns the attribute string or None if not found.
        """
        try:
            if not html_text:
                return None
                
            # Use regex to find the first table cell content in the header row
            # Look for the first <td> inside a <tr> with background color (header row)
            table_pattern = r'<tr[^>]*background[^>]*>.*?<td[^>]*>(.*?)</td>'
            match = re.search(table_pattern, html_text, re.DOTALL | re.IGNORECASE)
            
            if match:
                # Clean up the content (remove HTML tags, whitespace)
                attribute = match.group(1).strip()
                # Remove any remaining HTML tags
                attribute = re.sub(r'<[^>]+>', '', attribute).strip()
                return attribute if attribute else None
                
        except Exception as e:
            print(f"Error extracting HTML table attribute: {e}")
            
        return None
    
    def get_base_point(self):
        """
        Read the base point from base.kml in the base_kml directory.
        """
        base_kml_path = self.base_kml_dir / "base.kml"
        
        if not base_kml_path.exists():
            raise FileNotFoundError(f"Base KML file not found: {base_kml_path}")
            
        base_point = self.parse_kml_point(base_kml_path)
        if base_point is None:
            raise ValueError(f"Could not extract coordinates from base KML: {base_kml_path}")
            
        return base_point
    
    def get_destination_points(self):
        """
        Read all KML files from input_points_kml directory and extract all their points and attributes.
        Returns a list of dictionaries with point data including coordinates and HTML table attributes.
        """
        destination_points = []
        
        if not self.input_points_kml_dir.exists():
            print(f"Warning: Input points directory not found: {self.input_points_kml_dir}")
            return destination_points
            
        for kml_file in sorted(self.input_points_kml_dir.glob("*.kml")):
            print(f"Processing {kml_file.name}...")
            points = self.parse_all_kml_points(kml_file)
            
            for point_data in points:
                destination_points.append({
                    'filename': kml_file.stem,
                    'name': point_data['name'],
                    'coordinates': point_data['coordinates'],
                    'table_attribute': point_data['table_attribute'],
                    'kml_path': kml_file
                })
                
        return destination_points
    
    def create_dji_mission_kml(self, base_point, target_point, mission_name):
        """
        Create a DJI mission-compatible KML file with waypoints from base to target.
        Uses the format that works with DJI software - manually constructed XML.
        """
        # Clean the mission name for filename and XML
        clean_name = re.sub(r'[^\w\-_\s]', '_', mission_name)
        clean_name = re.sub(r'\s+', '_', clean_name.strip())
        
        # Create the KML content manually to match the working format exactly
        kml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">
<Document>
	<name>{clean_name}.kml</name>
	<StyleMap id="m_ylw-pushpin">
		<Pair>
			<key>normal</key>
			<styleUrl>#s_ylw-pushpin</styleUrl>
		</Pair>
		<Pair>
			<key>highlight</key>
			<styleUrl>#s_ylw-pushpin_hl</styleUrl>
		</Pair>
	</StyleMap>
	<Style id="s_ylw-pushpin">
		<IconStyle>
			<scale>1.1</scale>
			<Icon>
				<href>http://maps.google.com/mapfiles/kml/pushpin/ylw-pushpin.png</href>
			</Icon>
			<hotSpot x="20" y="2" xunits="pixels" yunits="pixels"/>
		</IconStyle>
	</Style>
	<Style id="s_ylw-pushpin_hl">
		<IconStyle>
			<scale>1.3</scale>
			<Icon>
				<href>http://maps.google.com/mapfiles/kml/pushpin/ylw-pushpin.png</href>
			</Icon>
			<hotSpot x="20" y="2" xunits="pixels" yunits="pixels"/>
		</IconStyle>
	</Style>
	<Placemark>
		<name>{clean_name}</name>
		<styleUrl>#m_ylw-pushpin</styleUrl>
		<LineString>
			<tessellate>1</tessellate>
			<coordinates>
				{base_point[0]},{base_point[1]},{base_point[2]} {target_point[0]},{target_point[1]},{target_point[2]} 
			</coordinates>
		</LineString>
		<atom:link rel="app" href="https://www.google.com/earth/about/versions/#earth-pro" title="Google Earth Pro 7.3.6.10201"></atom:link>
	</Placemark>
</Document>
</kml>'''
        
        return kml_content
    
    def process_all_points(self):
        """
        Main processing function that creates DJI mission files for all destination points.
        """
        try:
            # Get base point
            print("Reading base point...")
            base_point = self.get_base_point()
            print(f"Base point: {base_point}")
            
            # Get all destination points
            print("Reading destination points...")
            destination_points = self.get_destination_points()
            
            if not destination_points:
                print("No destination points found in input_points_kml directory.")
                return
                
            print(f"\nFound {len(destination_points)} destination points:")
            for i, point_data in enumerate(destination_points):
                attr_info = f" (attribute: {point_data['table_attribute']})" if point_data['table_attribute'] else ""
                print(f"  - {point_data['name']}: {point_data['coordinates']}{attr_info}")
            
            # Create mission KML files with numbered filenames
            print("\nCreating DJI mission files...")
            for i, point_data in enumerate(destination_points, 1):
                kml_content = self.create_dji_mission_kml(
                    base_point, 
                    point_data['coordinates'], 
                    point_data['name']
                )
                
                # Generate filename with leading zeros and table attribute
                file_number = f"{i:03d}"  # 001, 002, 003, etc.
                
                # Build filename components
                filename_parts = [file_number]
                if point_data['table_attribute']:
                    # Clean the attribute for use in filename (remove special characters)
                    clean_attribute = re.sub(r'[^\w\-_\s]', '_', point_data['table_attribute'])
                    clean_attribute = re.sub(r'\s+', '_', clean_attribute.strip())  # Replace spaces with underscores
                    filename_parts.append(clean_attribute)
                
                filename = "_".join(filename_parts) + ".kml"
                output_file = self.output_paths_dir / filename
                
                # Write the KML content directly to file
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(kml_content)
                    
                print(f"Created: {output_file}")
            
            print(f"\nProcessing complete! Created {len(destination_points)} mission files.")
            
        except Exception as e:
            print(f"Error during processing: {e}")
            sys.exit(1)


def main():
    """Main entry point of the script."""
    script_dir = Path(__file__).parent
    processor = KMLPointProcessor(script_dir)
    processor.process_all_points()


if __name__ == "__main__":
    main()