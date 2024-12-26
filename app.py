import os
import json
import ee
from flask import Flask, request, render_template, jsonify, send_file
import geopandas as gpd
from shapely.geometry import Polygon
from zipfile import ZipFile

# Initialize the Flask app
app = Flask(__name__)

# Authenticate using the service account key file
key_file = "service_account.json"  # Replace with the correct file path
credentials = ee.ServiceAccountCredentials(None, key_file)
ee.Initialize(credentials)


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        try:
            # Get user inputs
            longitude = float(request.form["longitude"])
            latitude = float(request.form["latitude"])
            start_date = request.form["start_date"]
            end_date = request.form["end_date"]
            max_cloud_cover = int(request.form["max_cloud_cover"])

            # Process Sentinel-2 data
            output_file = process_sentinel_data(longitude, latitude,
                                                start_date, end_date,
                                                max_cloud_cover)

            # Return the zipped shapefile as a downloadable file
            return send_file(output_file, as_attachment=True)

        except Exception as e:
            return jsonify({"error": str(e)})

    # Render the input form
    return render_template("index.html")


def process_sentinel_data(longitude, latitude, start_date, end_date,
                          max_cloud_cover):
    """
    Process Sentinel-2 data using Earth Engine and export the tile coordinates as a shapefile.
    """
    # Create a point geometry for the input coordinates
    input_geometry = ee.Geometry.Point([longitude, latitude])

    # Retrieve Sentinel-2 ImageCollection
    collection = ee.ImageCollection("COPERNICUS/S2_HARMONIZED") \
        .filterBounds(input_geometry) \
        .filterDate(start_date, end_date) \
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", max_cloud_cover))

    # Get the unique tile IDs
    tile_ids = collection.aggregate_array("MGRS_TILE").distinct().getInfo()

    # Prepare output folder
    output_folder = "Sentinel_Tile_Shapefiles"
    os.makedirs(output_folder, exist_ok=True)

    # Loop through each tile ID and create shapefiles
    for tile_id in tile_ids:
        tile_geometry = collection.filter(ee.Filter.eq("MGRS_TILE",
                                                       tile_id)).geometry()
        coords = tile_geometry.bounds().coordinates().get(0).getInfo()
        polygon = Polygon([(coord[0], coord[1]) for coord in coords])

        gdf = gpd.GeoDataFrame({"tile_id": [tile_id]},
                               geometry=[polygon],
                               crs="EPSG:4326")

        shapefile_name = os.path.join(output_folder, f"{tile_id}.shp")
        gdf.to_file(shapefile_name, driver="ESRI Shapefile", engine="pyogrio")

    # Zip the shapefiles
    zip_filename = os.path.join(output_folder, "Sentinel_Tile_Shapefiles.zip")
    with ZipFile(zip_filename, "w") as zipf:
        for root, _, files in os.walk(output_folder):
            for file in files:
                zipf.write(os.path.join(root, file),
                           arcname=os.path.relpath(os.path.join(root, file),
                                                   output_folder))

    return zip_filename


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
