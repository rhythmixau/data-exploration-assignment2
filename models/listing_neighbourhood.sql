with source as (
    select neighbourhood_group, neighbourhood, price from {{ ref('bronze_listings') }}
),
    nta_neighbourhoods AS (
      SELECT neighbourhood_group, neighbourhood, ntaname
      FROM {{ ref('nta_neighbourhoods') }} WHERE row_count = 1
    ),
    new_neighbourhoods AS (
        select s.neighbourhood_group, s.neighbourhood, n.ntaname as nta_neighbourhood, s.price
        from source s
        join nta_neighbourhoods n on n.neighbourhood = s.neighbourhood
            and n.neighbourhood_group = s.neighbourhood_group
    )
select nta_neighbourhood,
       neighbourhood_group,
       min(price) as min_price,
       max(price) as max_price,
       median(price) as median_price,
       count(price) as num_listings
    from new_neighbourhoods
    group by nta_neighbourhood, neighbourhood_group
    order by neighbourhood_group, nta_neighbourhood
