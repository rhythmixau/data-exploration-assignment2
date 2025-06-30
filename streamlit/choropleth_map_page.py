import streamlit as st
import plotly.express as px
import duckdb
import geopandas

from contants import duckdb_path, geojson_path

# stg_nyc_neighbourhoods

with duckdb.connect(duckdb_path) as conn:
    print(f"Geo file: {geojson_path}")
    geo_df = geopandas.read_file(geojson_path)

    listings_summary_df = conn.sql("SELECT * FROM database.main.listing_neighbourhood").df()

fig = px.choropleth_map(
    listings_summary_df,                            # Your aggregated data
    geojson=geo_df,                      # The GeoJSON file with the shapes
    locations='neighbourhood',                     # The column in your data that matches the GeoJSON key
    featureidkey='properties.ntaname',        # The path to the key in the GeoJSON's properties
    color='median_price',                     # The column with the values to map
    color_continuous_scale="Viridis",         # A nice color scale
    range_color=(10, 300),                    # Set the range of the color scale for better contrast
    # mapbox_style="carto-positron",            # Use a clean, light map background
    zoom=9.5,                                 # Set the initial zoom level
    center={"lat": 40.7128, "lon": -74.0060}, # Center the map on NYC
    opacity=0.6,                              # Set the opacity of the colored areas
    labels={'median_price': 'Median Price ($)'} # Prettier hover labels
)
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
st.plotly_chart(fig, key="Bronze Listings", on_select="rerun")