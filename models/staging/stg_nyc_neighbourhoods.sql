with source as (
    select * from ST_Read('data/nyc_neighbourhoods_geo.geojson')
)
select * from source
