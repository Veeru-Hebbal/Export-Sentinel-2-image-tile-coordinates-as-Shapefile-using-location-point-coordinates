from flask import Flask, request, render_template, jsonify, send_file
import ee
import geopandas as gpd
from shapely.geometry import Polygon, Point
from zipfile import ZipFile
import os

# Initialize the Flask app
app = Flask(__name__)

# Authenticate and initialize Google Earth Engine
ee.Authenticate()
ee.Initialize(project="gee-project-lulc")


@app.route("/")
def index():
    """Render the main page with input form."""
    return render_template("index.html")


@app.route("/process", methods=["POST"])
def process():
    """Process user inputs and fetch Sentinel-2 data."""
    try:
        # Get input from the form
        longitude = float(request.form["longitude"])
        latitude = float(request.form["latitude"])
        start_date = request.form["start_date"]
        end_date = request.form["end_date"]
        max_cloud_cover = float(request.form["max_cloud_cover"])

        # Define input coordinates
        input_coordinates = [longitude, latitude]
        input_geometry = ee.Geometry.Point(input_coordinates)

        # Retrieve Sentinel-2 ImageCollection for the given parameters
        collection = ee.ImageCollection("COPERNICUS/S2_HARMONIZED") \
            .filterBounds(input_geometry) \
            .filterDate(start_date, end_date) \
            .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", max_cloud_cover))

        # Check if collection is empty
        if collection.size().getInfo() == 0:
            return jsonify({"status": "error", "message": "No Sentinel-2 images available for the specified parameters."})

        # Get the first image to retrieve MGRS tile
        first_image = collection.first()
        mgrs_tile = first_image.get("MGRS_TILE").getInfo()

        # Fetch image metadata
        image_list = collection.toList(collection.size())
        image_metadata = []
        for i in range(image_list.size().getInfo()):
            img = ee.Image(image_list.get(i))
            image_id = img.get("system:index").getInfo()  # Image name
            cloud_cover = img.get("CLOUDY_PIXEL_PERCENTAGE").getInfo()  # Cloud cover percentage
            acquisition_date = ee.Date(img.get("system:time_start")).format("YYYY-MM-dd").getInfo()  # Date
            image_metadata.append({"image_id": image_id, "date": acquisition_date, "cloud_cover": cloud_cover})

        # Generate shapefile for the MGRS tile
        tile_geometry = collection.filter(ee.Filter.eq("MGRS_TILE", mgrs_tile)).geometry()
        coords = tile_geometry.bounds().coordinates().get(0).getInfo()
        polygon = Polygon([(coord[0], coord[1]) for coord in coords])

        # Create a GeoDataFrame
        gdf = gpd.GeoDataFrame(
            {"tile_id": [mgrs_tile]},  # Add tile ID as an attribute
            geometry=[polygon],
            crs="EPSG:4326"  # Set the coordinate reference system to WGS84
        )

        # Save the GeoDataFrame as a shapefile in the downloads folder
        downloads_folder = os.path.join(os.getcwd(), "downloads")
        os.makedirs(downloads_folder, exist_ok=True)
        shapefile_name = f"{mgrs_tile}.shp"
        gdf.to_file(os.path.join(downloads_folder, shapefile_name), driver="ESRI Shapefile")

        # Zip the shapefile
        zip_filename = os.path.join(downloads_folder, f"{mgrs_tile}.zip")
        with ZipFile(zip_filename, "w") as zipf:
            for root, _, files in os.walk(downloads_folder):
                for file in files:
                    if file.startswith(mgrs_tile):
                        zipf.write(os.path.join(root, file), arcname=os.path.basename(file))

        # Return JSON response with a link to download the shapefile
        return jsonify({
            "status": "success",
            "mgrs_tile": mgrs_tile,
            "image_metadata": image_metadata,
            "shapefile_download": f"/download/{mgrs_tile}.zip"
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route("/download/<filename>")
def download(filename):
    """Provide the shapefile download."""
    downloads_folder = os.path.join(os.getcwd(), "downloads")
    filepath = os.path.join(downloads_folder, filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    else:
        return jsonify({"status": "error", "message": "File not found."})


if __name__ == "__main__":
    app.run(debug=True)
