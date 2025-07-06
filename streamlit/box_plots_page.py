import duckdb
import numpy as np
import plotly.graph_objects as go

import streamlit as st
from contants import duckdb_path

num_rows_1 = 0
colours = {
    "Bronx": "#9b5de5",
    "Brooklyn": "#f15bb5",
    "Manhattan": "#fee440",
    "Queens": "#00bbf9",
    "Staten Island": "#00f5d4",
}

with duckdb.connect(duckdb_path) as conn:
    neighbourhoods_df = conn.sql("""
    SELECT distinct neighbourhood_group 
    FROM database.main.listing_neighbourhood 
    order by neighbourhood_group
    """).df()

with st.container(height=600):
    with duckdb.connect(duckdb_path) as conn:
        listings_df = conn.sql("""
        SELECT listing_id, listing_title, neighbourhood, neighbourhood_group, price 
        FROM database.main.stg_listings 
        order by neighbourhood_group, neighbourhood
        """).df()
    num_rows_1 = listings_df.shape[0]
    col1, col2 = st.columns(2)
    with col1:
        st.header("Raw Data")
    with col2:
        st.metric(label="No. of Listings", value=f"{listings_df.shape[0]} rows")

    listings_df = listings_df.sort_values(by=['neighbourhood_group', 'neighbourhood', 'price'])
    fig = go.Figure()
    for group in neighbourhoods_df["neighbourhood_group"]:
        group_listings = listings_df[listings_df["neighbourhood_group"] == group]
        fig.add_trace(go.Box(
            x=group_listings["price"],
            y=group_listings["neighbourhood"],
            name=group,
            marker_color=colours[group]
        ))
    fig.update_layout(
        xaxis=dict(title=dict(text="Listings price"), zeroline=False),
        boxmode="group"
    )
    fig.update_traces(orientation="h")

    st.plotly_chart(fig, key="listings", on_select="rerun")
    st.text("Check if any outliers could be detected")
st.divider()

problematic_listings = listings_df[listings_df["listing_id"].isin([3928833, 2953058, 15455305, 17537893, 18051877, 18616208, 22296097, 24535740, 22296197,
                          30035166, 33998396, 27629043, 33007610, 2952861, 25018204, 2276383, 23373090, 34592851,
                          22295960, 23372850, 8736827, 4823682])]

with st.container(border=True):
    st.subheader("Data Cleaning and Reasons")
    st.markdown("""
    The box plot above reveals several potential outliers. A closer investigation shows that these are not typical 
    residential listings. For example, listing 18051877 in Randall Manor, Staten Island, is a location available 
    for film and photography shoots, not a residential accommodation. The dataset also includes other non-residential 
    properties, such as animal accommodations and various event spaces.
""")
    st.markdown("""
    Since the focus of this analysis is on residential stays, these non-relevant listings are to be excluded to avoid 
    skewing the results.""")
    st.dataframe(problematic_listings)
    st.subheader("What to do with these listings?")
    st.markdown("First, a new boolean column named is_special_property is initialized with a default value of False.")
    st.markdown("Next, several data cleaning steps are performed. All listings with a price below $10 are excluded, as "
                "this is below Airbnb's minimum allowable price. We also exclude several categories of listings that "
                "do not represent typical residential accommodations, as their inclusion would skew the analysis. "
                "These exclusions include specific listings identified as:")
    st.markdown("""
    * Filming locations
    * Gallery and event spaces
    * Yachts
    * Photography studios
    * Spas and saunas
    * Animal accommodations
    """)
    st.markdown("""
    Finally, while the dataset contains some very expensive properties, these are considered genuine listings and 
    are intentionally kept. Removing these valid, high-end listings would introduce bias, leading to an analysis 
    that does not accurately reflect the full spectrum of the market.
    """)

st.divider()

with st.container(height=600):
    with duckdb.connect(duckdb_path) as conn:
        listings_df = conn.sql("""
        SELECT listing_id, neighbourhood, neighbourhood_group, price 
        FROM database.main.bronze_listings 
        WHERE NOT is_special_property
        order by neighbourhood_group, neighbourhood
        """).df()

    col1, col2 = st.columns(2)
    with col1:
        st.header("Cleansed Data")
    with col2:
        num_rows_2 = listings_df.shape[0]
        st.metric(label="No. of Listings", value=f"{listings_df.shape[0]} rows", delta=f"{num_rows_2 - num_rows_1} rows")

    neighbourhood_groups = np.sort(listings_df["neighbourhood_group"].unique())
    listings_df = listings_df.sort_values(by=['neighbourhood_group', 'neighbourhood', 'price'])
    fig = go.Figure()
    for group in neighbourhood_groups:
        group_listings = listings_df[listings_df["neighbourhood_group"] == group]
        fig.add_trace(go.Box(
            x=group_listings["price"],
            y=group_listings["neighbourhood"],
            name=group,
            marker_color=colours[group]
        ))
    fig.update_layout(
        xaxis=dict(title=dict(text="Listings price"), zeroline=False),
        boxmode="group"
    )
    fig.update_traces(orientation="h")

    st.plotly_chart(fig, key="cleansed-listings", on_select="rerun")
