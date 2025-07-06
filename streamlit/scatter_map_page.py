import duckdb
import pandas as pd
import plotly.express as px
from sklearn.preprocessing import MinMaxScaler

import streamlit as st
from contants import duckdb_path

with duckdb.connect(duckdb_path) as conn:
    neighbourhood_groups = conn.sql(
        "SELECT distinct neighbourhood_group FROM database.main.neighbourhood order by neighbourhood_group").df()
    all_row = pd.DataFrame({"neighbourhood_group": ["all"]})
    neighbourhood_groups = pd.concat([all_row, neighbourhood_groups], ignore_index=True)

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
        with duckdb.connect(duckdb_path) as conn:
            query = f"""
            SELECT listing_id, neighbourhood, neighbourhood_group, latitude, longitude, 
            price, number_of_reviews, listing_title 
            FROM database.main.bronze_listings 
            WHERE NOT is_special_property and price >= {start_price} and price <= {end_price}
            order by neighbourhood_group, neighbourhood""" if selected_group == "all" else f"""
            SELECT listing_id, neighbourhood, neighbourhood_group, latitude, longitude, 
            price, number_of_reviews, listing_title 
            FROM database.main.bronze_listings 
            WHERE NOT is_special_property and neighbourhood_group = '{selected_group}' and price >= {start_price} and price <= {end_price}
            order by neighbourhood_group, neighbourhood
            """
            listings_df = conn.sql(query).df()

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

        # Replace the null value with 0
        listings_df["number_of_reviews"] = listings_df["number_of_reviews"].fillna(0)

        scaler = MinMaxScaler(feature_range=(2, 20))
        listings_df["marker_size"] = scaler.fit_transform(listings_df[["number_of_reviews"]])

        st.subheader("Listings below $500")
        mcol1, mcol2, mcol3, mcol4 = st.columns(4)
        with mcol1:
            st.metric(label="Minimum price", value=min_price)
        with mcol2:
            st.metric(label="Maximum price", value=max_price)
        with mcol3:
            st.metric(label="Median price", value=median_price)
        with mcol4:
            st.metric(label="Number of listings", value=num_listings)

        st.divider()
        if min_price_high_end > 0 and max_price_high_end > 0:
            st.subheader("Listings $500 and above")
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
                             size="marker_size",
                             color_continuous_scale=["#3a86ff", "#8338ec", "#ff006e"],
                             height=900,
                             size_max=15,
                             zoom=12,
                             hover_data=["listing_id", "price", "neighbourhood", "neighbourhood_group",
                                         "number_of_reviews", "listing_title"],
                             opacity=0.8,
                             )

        st.plotly_chart(fig, key="Bronze Listings", on_select="rerun")

        st.subheader("Conclusions")
        st.markdown("#### 1.")
        st.markdown(
            "> If I were to go on a holiday and wanted to stay right where everything is happening, Manhattan is the "
            "obvious choice. It is more crowded and more expensive; however, the prices do get cheaper as you move "
            "northward toward the Bronx.")
        st.markdown("> **Note:** It appears that listing with ID 36001911 might contain invalid geo data, as it is in the "
            "water. Its title doesn't indicate that it is a yacht listing, so I'll assume this is a mistake that "
            "requires further investigation.")

        st.markdown("#### 2.")
        st.markdown(
            "> If I were to go there with my family for a weekend holiday, looking for a bit more space and "
            "quieter neighbourhood, I would choose to stay on Staten Island and then catch a ferry to Manhattan "
            "where all the main tourist attractions are.")
        st.markdown("#### 3.")
        st.markdown(
            "> If budget is the main constraint but I still want to be near Manhattan, then Bronx would be a "
            "good choice. The median price for most neighbourhoods in Bronx are below $100.")

    else:
        st.text("Please, select the neighbourhood and click the submit button")

