with source as (
    select * from {{ ref('airbnb_nyc_2019') }}
),
    renamed as (
        select
            id as listing_id,
            name as listing_title,
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
        from source
    )
select * from renamed