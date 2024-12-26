# Sentinel-2 Image Tile Export Tool

This Flask-based web application allows users to process Sentinel-2 satellite imagery from Google Earth Engine (GEE) and export the corresponding tile coordinates as shapefiles. The shapefiles are provided as a downloadable zip file.

## Features

- Input geographical coordinates (longitude, latitude) and time range for Sentinel-2 data.
- Filter images based on cloud cover percentage.
- Export the boundaries of Sentinel-2 image tiles as shapefiles.
- Download the generated shapefiles as a zip file.

---

## Prerequisites

Before running this application, ensure you have the following installed:

1. **Python 3.9 or higher**
2. **Google Earth Engine (GEE) API**
3. **Service account credentials** (JSON key file)
4. **Required Python libraries** (listed in `requirements.txt`):
   - Flask
   - earthengine-api
   - geopandas
   - shapely
   - pyogrio

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/<your-repo>/Sentinel-2-Tile-Export.git
   cd Sentinel-2-Tile-Export

2. Install the dependencies:
pip install -r requirements.txt

3. Add your Google Earth Engine service account key:
   * Place the service_account.json file in the project directory.
   * Ensure the file path in app.py matches the file location:
key_file = "service_account.json"

4. Project Structure:
/Sentinel-2-Tile-Export
├── app.py                  # Main Flask application
├── requirements.txt        # List of Python dependencies
├── templates/
│   └── index.html          # HTML template for the web form

5. Usage:
Enter the following parameters in the form:

Longitude: The longitude of the point of interest (77.200).
Latitude: The latitude of the point of interest (13.303).
Start Date: The starting date for image collection (DD-MM-YYYY).
End Date: The ending date for image collection (DD-MM-YYYY).
Max Cloud Cover (%): Maximum allowable cloud cover percentage.
Click Submit to process the data.

Download the resulting zip file containing shapefiles for the Sentinel-2 tiles.

6. License:
This project is licensed under the MIT License. See the LICENSE file for details.

7. Contact info:
For any issues or feature requests, feel free to contact:
Name: Dr. Virupaksha H S
emailID: virupaksha.773@gmail.com
gitHub: https://github.com/Veeru-Hebbal

Thank You!
