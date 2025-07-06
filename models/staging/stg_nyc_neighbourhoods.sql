with source as (
    select * from ST_Read('streamlit/2020_nta_nyc.geojson')
)
select * from source
