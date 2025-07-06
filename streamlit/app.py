import streamlit as st

st.set_page_config(layout="wide")
st.title('Data Exploration - Assignment 2')
st.subheader('by Jack Toke')

pg = st.navigation({"Home": [
    st.Page("box_plots_page.py", title="Step 1 - Box Plots"),
    st.Page("choropleth_map_page.py", title="Step 2 - Choropleth Map"),
    st.Page("scatter_map_page.py", title="Step 3 - Scatter Map"),
]})

pg.run()