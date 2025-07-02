import streamlit as st
import plotly.express as px
import duckdb
import geopandas
import plotly.graph_objects as go

from contants import duckdb_path, geojson_path

with duckdb.connect(duckdb_path) as conn:
    print(f"Geo file: {geojson_path}")
    geo_df = geopandas.read_file(geojson_path)

    listings_summary_df = conn.sql("SELECT * FROM database.main.listing_neighbourhood").df()
    problem_neighbourhoods = conn.sql("""
    LOAD spatial;
    WITH neighbourhoods AS (
      SELECT distinct b.neighbourhood, 
      n.ntaname, 
      b.neighbourhood_group
      FROM bronze_listings b
      LEFT JOIN stg_nyc_neighbourhoods n ON n.ntaname ILIKE '%' || b.neighbourhood  || '%' AND n.boroname = b.neighbourhood_group
    ),
      neighbourhoods_agg AS (
        SELECT ntaname, COUNT(ntaname) num_neighbourhood
        FROM neighbourhoods
        GROUP BY ntaname
      ),
      problem_neighbourhoods AS (
      SELECT n.neighbourhood, n.ntaname, n.neighbourhood_group
      FROM neighbourhoods n
      JOIN neighbourhoods_agg a ON a.ntaname = n.ntaname
      WHERE num_neighbourhood >= 2
      )
    SELECT neighbourhood, ntaname, neighbourhood_group 
      FROM problem_neighbourhoods
    ORDER BY neighbourhood_group, ntaname
    """).df()
    problem_neighbourhoods2 = conn.sql("""
    SELECT * FROM database.main.nta_neighbourhoods WHERE total_count > 1
    """).df()
    borough_summary_df = conn.sql("""
    SELECT neighbourhood_group, MEDIAN(median_price) median_price, SUM(num_listings) num_listings 
    FROM database.main.listing_neighbourhood 
    GROUP BY neighbourhood_group 
    ORDER BY neighbourhood_group
    """).df()

with st.container(border=True):
    st.markdown("### Overview")
    col1, col2 = st.columns(2)
    with col1:
        borough_price_fig = go.Figure()
        borough_price_fig.add_trace(go.Bar(
            x=borough_summary_df['neighbourhood_group'],
            y=borough_summary_df['median_price'],
            name="Median Price",
            text=borough_summary_df['median_price'],
            marker_color="#3a86ff"
        ))
        borough_price_fig.update_layout(barmode="group", xaxis_tickangle=0, xaxis=dict(
            title=dict(text="Median Price (AUD$) by Borough")
        ),)
        st.plotly_chart(borough_price_fig, key="NYC AirBnb Price", on_select="rerun")
    with col2:
        borough_count_fig = go.Figure()
        borough_count_fig.add_trace(go.Bar(
            x=borough_summary_df['neighbourhood_group'],
            y=borough_summary_df['num_listings'],
            name="Number of Listings",
            text=borough_summary_df['num_listings'],
            marker_color="#8338ec"
        ))
        borough_count_fig.update_layout(barmode="group", xaxis_tickangle=0, xaxis=dict(
            title=dict(text="# Listings by Borough")
        ),)
        st.plotly_chart(borough_count_fig, key="NYC - AirBnb #Listings", on_select="rerun")

max_median_price = listings_summary_df["median_price"].max()

fig = px.choropleth_map(
    listings_summary_df,                            # Your aggregated data
    geojson=geo_df,                      # The GeoJSON file with the shapes
    locations='nta_neighbourhood',                     # The column in your data that matches the GeoJSON key
    featureidkey='properties.ntaname',        # The path to the key in the GeoJSON's properties
    color='median_price',                     # The column with the values to map
    color_continuous_scale=["#ffbe0b", "#ff006e"],         # A nice color scale
    range_color=(10, max_median_price),                    # Set the range of the color scale for better contrast
    # mapbox_style="carto-positron",            # Use a clean, light map background
    zoom=9.5,                                 # Set the initial zoom level
    center={"lat": 40.7128, "lon": -74.0060}, # Center the map on NYC
    opacity=0.6,                              # Set the opacity of the colored areas
    labels={'median_price': 'Median Price ($)'}, # Prettier hover labels
    height=900,
    hover_data=["nta_neighbourhood", "neighbourhood_group", "median_price", "min_price", "max_price", "num_listings"],
)
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
with st.container(border=True):
    st.plotly_chart(fig, key="Bronze Listings", on_select="rerun")

st.html("<br/>")
st.dataframe(listings_summary_df)
st.divider()

with st.container(border=True):
    st.subheader("Challenges")
    st.markdown("""1. A key challenge was that the dataset provided by QUT lacked the geospatial data necessary to 
    create choropleth maps. To resolve this, I sourced official boundary data from the [the City of New York](https://data.cityofnewyork.us/City-Government/2020-Neighborhood-Tabulation-Areas-NTAs-/9nt8-h7nd/about_data).
    """)
    st.markdown("""
    2. However, a data alignment issue arose because the neighborhood names in the QUT dataset did not directly match 
    the official areas in the geospatial data. For example, the 'Concourse' and 'Concourse Village' neighborhoods in 
    the QUT data correspond to a single official area named 'Concourse-Concourse Village'.
    To overcome this mismatch, the data was aggregated using the official Neighbourhood Tabulation Area (NTA) names as 
    the common identifier, rather than the colloquial neighborhood names.
    """)
    st.dataframe(problem_neighbourhoods)
    st.markdown("""
    3. The above solution resolved most of the issues, except that some neighborhoods, as shown below, are divided 
    into more than one neighborhood in the National Tabulation Area dataset. To resolve this, we will choose the 
    first matched NTA name for each neighborhood and use it to create the heatmap. For this, we will have to accept 
    that the data will be skewed towards some neighborhoods.
    """)
    st.dataframe(problem_neighbourhoods2)


with st.container(border=True):
    st.subheader("Analysis and observation")
    st.markdown("1. In general, the heatmap indicates that the more pink hue a neighborhood's color has, the higher "
                "the median price.")
    st.markdown("2. While the heat map indicates that 'Fort Wadsworth' has the highest median price, this figure is "
                "based on only a single property listing, making it a statistical anomaly.")
    st.markdown("3. A more reliable observation is that certain neighborhoods in Queens—specifically Breezy Point "
                "and Rockaway Beach—and the borough of Manhattan generally command the highest overall median price. "
                "Furthermore, Manhattan also has the greatest density of properties, with the highest number of "
                "listings per square kilometer.")

