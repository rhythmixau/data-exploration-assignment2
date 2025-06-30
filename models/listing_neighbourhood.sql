with source as (
    select * from {{ ref('bronze_listings') }}
),
    higher_end as (
        select
            neighbourhood,
            neighbourhood_group,
            min(price) as high_end_min_price,
            max(price) as high_end_max_price,
            median(price) as high_end_median_price,
            count(price) as high_end_num_listings
        from source
        where price >= 1000
        group by neighbourhood, neighbourhood_group
        order by neighbourhood, neighbourhood_group
    ),
    lower_end as (
        select neighbourhood,
       neighbourhood_group,
       min(price) as min_price,
       max(price) as max_price,
       median(price) as median_price,
       count(price) as num_listings
    from source
    where price < 1000
    group by neighbourhood, neighbourhood_group
    order by neighbourhood_group, neighbourhood
    )
    select l.neighbourhood, l.neighbourhood_group, l.min_price, l.max_price, l.median_price, l.num_listings,
           h.high_end_min_price, h.high_end_max_price, h.high_end_median_price, h.high_end_num_listings
           from lower_end l
    left join higher_end h on h.neighbourhood = l.neighbourhood


