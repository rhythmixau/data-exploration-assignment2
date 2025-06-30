from pathlib import Path
import streamlit as st
import duckdb
import numpy as np
import plotly.graph_objects as go

duckdb_path = Path(__file__).parent.parent / "database.duckdb"
num_rows_1 = 0
with st.container(height=600):
    with duckdb.connect(duckdb_path) as conn:
        listings_df = conn.sql("""
        SELECT listing_id, neighbourhood, neighbourhood_group, price 
        FROM database.main.stg_listings 
        order by neighbourhood_group, neighbourhood
        """).df()
    num_rows_1 = listings_df.shape[0]
    col1, col2 = st.columns(2)
    with col1:
        st.header("Raw Data")
    with col2:
        st.metric(label="No. of Listings", value=f"{listings_df.shape[0]} rows")
    st.text("Check if any outliers could be detected")

    neighbourhood_groups = listings_df["neighbourhood_group"].unique()
    c = ['hsl('+str(h)+',50%'+',50%)' for h in np.linspace(0, 360, len(neighbourhood_groups))]

    print(f"Neighbourhood groups: {neighbourhood_groups}")
    listings_df = listings_df.sort_values(by=['neighbourhood_group', 'neighbourhood', 'price'])

    fig = go.Figure()
    colors = dict(zip(neighbourhood_groups, c))

    for group in neighbourhood_groups:
        group_listings = listings_df[listings_df["neighbourhood_group"] == group]
        fig.add_trace(go.Box(
            x=group_listings["price"],
            y=group_listings["neighbourhood"],
            name=group,
            marker_color=colors[group]
        ))
    fig.update_layout(
        xaxis=dict(title=dict(text="Listings price"), zeroline=False),
        boxmode="group"
    )
    fig.update_traces(orientation="h")

    st.plotly_chart(fig, key="listings", on_select="rerun")

st.divider()

with st.container():
    st.subheader("Changes")
    st.markdown("1. Removed all listings with price below `$10`, since AirBnb minimum price is `$10`")
    st.markdown("2. Removed filming location listings (3928833, 2953058, 15455305, 17537893, 18051877, 18616208, 24535740, 8736827)")
    st.markdown("3. Removed gallery space for event (22296097, 23373090, 24535740, 2276383, 34592851, 4777903, 22295960, 23372850)")
    st.markdown("4. Removed yatch listings (27629043, 33007610)")
    st.markdown("5. Removed photography location (2952861)")
    st.markdown("6. Removed Spa and Sauna listing (25018204)")
    st.markdown("7. Removed animal accommodation (4823682)")

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

    neighbourhood_groups = listings_df["neighbourhood_group"].unique()
    c = ['hsl('+str(h)+',50%'+',50%)' for h in np.linspace(0, 360, len(neighbourhood_groups))]

    print(f"Neighbourhood groups: {neighbourhood_groups}")
    listings_df = listings_df.sort_values(by=['neighbourhood_group', 'neighbourhood', 'price'])

    fig = go.Figure()
    colors = dict(zip(neighbourhood_groups, c))

    for group in neighbourhood_groups:
        group_listings = listings_df[listings_df["neighbourhood_group"] == group]
        fig.add_trace(go.Box(
            x=group_listings["price"],
            y=group_listings["neighbourhood"],
            name=group,
            marker_color=colors[group]
        ))
    fig.update_layout(
        xaxis=dict(title=dict(text="Listings price"), zeroline=False),
        boxmode="group"
    )
    fig.update_traces(orientation="h")

    st.plotly_chart(fig, key="cleansed-listings", on_select="rerun")
