# Import packages
import pandas as pd
import requests
import numpy as np
import geopandas as gpd
from geopy.geocoders import Nominatim
import pandas as pd
import time
import warnings
warnings.filterwarnings('ignore')
# Get a geometry column
from shapely.geometry import Point
import folium

# Import csv file of services
services = pd.read_csv(r'C:\Users\thoma\Code\Projects\NCL Service Delivery\Service_partner_list_w_postcode.csv', index_col= [0])

# Create a list of postcodes from services
postcode_list = services['Postcode'].unique()

# Create an empty list for results
results = []

chunk_size = 10  # Define chunk size
for i in range(0, len(postcode_list), chunk_size):
    postcode_list_filtered = postcode_list[i:i+chunk_size]
    print(f"Collecting postcodes {i} to {i+len(postcode_list_filtered)-1}")

    response = requests.post(
        "https://api.postcodes.io/postcodes",
        json={"postcodes": postcode_list_filtered.tolist()}
    )

    if response.status_code == 200:
        results.append(response)
    else:
        print(f"Failed to retrieve data for chunk starting at index {i}: {response.status_code}")

# Turn the results into a list of pandas dataframes
results_dfs = [pd.json_normalize(i.json()['result'], sep='_')
for i in results]

# join all of our dataframes into a single dataframe.
postcodes_df = pd.concat(results_dfs)

# Keep useful columns from GPS data
postcode_subset = postcodes_df[['query', 'result_postcode', 'result_quality', 'result_eastings',
       'result_northings','result_nhs_ha',
       'result_longitude', 'result_latitude',
       'result_primary_care_trust',
       'result_lsoa', 'result_msoa',
       'result_outcode', 'result_parliamentary_constituency',
       'result_codes_admin_district',
       'result_codes_admin_ward',
       'result_codes_parish', 'result_codes_parliamentary_constituency',
       'result_codes_parliamentary_constituency_2024', 'result_codes_ccg',
       'result_codes_lsoa', 'result_codes_msoa']]

# Rename column
postcode_subset.rename(columns= {'result_postcode': 'Postcode'}, inplace= True)

# Merge original dataset
full_data = services.merge(postcode_subset, on= 'Postcode')

# Initialize the geolocator to seek team coordinates
geolocator = Nominatim(user_agent="geoapi")

# Create empty list
coordinates = []

# Loop through each row and collect coordinates
for index, row in full_data.iterrows():
    service = row['Team_name']
    postcode = row['Postcode']
    try:
        # Use service name and postcode to geocode
        location = geolocator.geocode(f"{postcode}", timeout=10)
        if location:
            coordinates.append({
                'Team_name': service,
                'Postcode': postcode,
                'Latitude': location.latitude,
                'Longitude': location.longitude
            })
            print(f"Processed: {service} - ({location.latitude}, {location.longitude})")
        else:
            print(f"Location not found for: {service}, {postcode}")
            coordinates.append({
                'Team_name': service,
                'Postcode': postcode,
                'Latitude': None,
                'Longitude': None
            })
    except Exception as e:
        print(f"Error for {service}, {postcode}: {e}")
        coordinates.append({
            'Team_name': service,
            'Postcode': postcode,
            'Latitude': None,
            'Longitude': None
        })
    time.sleep(1)  # Add delay to avoid rate-limiting

# Convert results to DataFrame
coordinates_df = pd.DataFrame(coordinates)

# Merge again with original dataset
data = full_data.merge(coordinates_df, on= 'Team_name')

# Drop duplicate column/rename other
data.drop(columns = 'Postcode_y', inplace = True)
data.rename(columns = {'Postcode_x': 'Postcode'}, inplace= True)

# Create a new geometry column that houses latitude/longitude coords
data['geometry'] = data.apply(
    lambda row: Point(row['Longitude'], row['Latitude']),
    axis=1
)

# Convert to GeoDataFrame
G_dataframe = gpd.GeoDataFrame(data, geometry='geometry')

# Define Coordinate Reference System (CRS)
G_dataframe.set_crs(epsg=4326, inplace=True)  # WGS84 CRS for latitude/longitude

# Change team name for map example
G_dataframe.iloc[34, G_dataframe.columns.get_loc("Team_name")] = 'Tavistock and Portman NHS Foundation Trust'

# Extract coordinates and team names
NCL_geo = [[row.geometry.y, row.geometry.x, row.Team_name] for _, row in G_dataframe.iterrows()]

# Create a Folium map centered around the first point
NCL_map = folium.Map(location=[51.6393, -0.1910], zoom_start=14)

# Loop through the coordinates and names
for lat, lon, name in NCL_geo:  # Unpack each entry in the list
    folium.Marker(
        location=[lat, lon],  # Latitude and Longitude
        popup=f"Service: {name}"  # Display name as popup
    ).add_to(NCL_map)

# Print map ~ 1
NCL_map

# Add a chloropleth example 
stats19_choro_gdf = gpd.read_file("stats_19_counts_by_msoa_normalised_3857.geojson")

# Create choropleth for rate cyclist collisions
choropleth = folium.Choropleth(
    geo_data = stats19_choro_gdf,
    data = stats19_choro_gdf,
    columns = ['MSOA11CD', 'cyclist_casualties_2018_2022_rate'],
    key_on = 'feature.properties.MSOA11CD',
    fill_color = 'OrRd',
    fill_opacity = 0.4,
    line_weight = 0.3,
    legend_name = 'Cyclist Casulaties',
    highlight = True,
    smooth_factor = 0 
)

# Add choropleth to map
choropleth.add_to(NCL_map)

# Print map ~ 2
NCL_map


