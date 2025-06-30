import streamlit as st
import plotly.express as px
import duckdb
from pathlib import Path

duckdb_path = Path(__file__).parent.parent / "database.duckdb"
with duckdb.connect(duckdb_path) as conn:
    neighbourhood_groups = conn.sql(
        "SELECT distinct neighbourhood_group FROM database.main.neighbourhood order by neighbourhood_group").df()

with st.form("my_form"):
    st.write("AirBnb Listings")
    col1, col2 = st.columns(2)
    with col1:
        selected_group = st.selectbox(
            "Neighbourhood Group",
            neighbourhood_groups["neighbourhood_group"],
        )
    with col2:
        start_price, end_price = st.select_slider(
            "Select a range of color wavelength",
            options=[
                "10",
                "100",
                "200",
                "500",
                "1000",
                "2000",
                "5000",
                "10000"
            ],
            value=("10", "10000"),
        )
    # Every form must have a submit button.
    submitted = st.form_submit_button("Submit")
    st.text(f"Neighbourhood Group:{selected_group}")
    if submitted:
        with st.container(height=1000):
            with duckdb.connect(duckdb_path) as conn:
                listings_df = conn.sql(f"""
                SELECT listing_id, neighbourhood, neighbourhood_group, latitude, longitude, price 
                FROM database.main.bronze_listings 
                WHERE NOT is_special_property and neighbourhood_group = '{selected_group}' and price >= {start_price} and price <= {end_price}
                order by neighbourhood_group, neighbourhood
                """).df()

            low_end_listings = listings_df[listings_df["price"] < 500]
            min_price = low_end_listings["price"].min()
            max_price = low_end_listings["price"].max()
            median_price = low_end_listings["price"].median()
            num_listings = low_end_listings["listing_id"].count()

            high_end_listings = listings_df[listings_df["price"] >= 500]
            min_price_high_end = high_end_listings["price"].min()
            max_price_high_end = high_end_listings["price"].max()
            median_price_high_end = high_end_listings["price"].median()
            num_high_end_listings = high_end_listings["listing_id"].count()

            mcol1, mcol2, mcol3, mcol4 = st.columns(4)
            with mcol1:
                st.metric(label="Minimum price", value=min_price)
            with mcol2:
                st.metric(label="Maximum price", value=max_price)
            with mcol3:
                st.metric(label="Median price", value=median_price)
            with mcol4:
                st.metric(label="Number of listings", value=num_listings)

            hcol1, hcol2, hcol3, hcol4 = st.columns(4)
            with hcol1:
                st.metric(label="Minimum price (high end)", value=min_price_high_end)
            with hcol2:
                st.metric(label="Maximum price (high end)", value=max_price_high_end)
            with hcol3:
                st.metric(label="Median of high end listings", value=median_price_high_end)
            with hcol4:
                st.metric(label="Num. of high end listings", value=num_high_end_listings)

            fig = px.scatter_map(listings_df,
                                 lat="latitude",
                                 lon="longitude",
                                 color="price",
                                 color_continuous_scale=px.colors.cyclical.IceFire,
                                 height=900,
                                 size_max=15,
                                 zoom=12,
                                 )

            st.plotly_chart(fig, key="Bronze Listings", on_select="rerun")
    else:
        st.text("Please, select the neighbourhood and click the submit button")



