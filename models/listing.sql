with staged_listings as (
    select * from {{ ref('cleansed_listings') }}
)
select
    listing_id,
    listing_title,
    host_id,
    host_name,
    neighbourhood_group,
    neighbourhood,
    latitude,
    longitude,
    room_type,
    price,
    minimum_nights,
    number_of_reviews,
    last_review,
    reviews_per_month,
    calculated_host_listings_count,
    availability_365
from staged_listings
order by neighbourhood_group, neighbourhood
