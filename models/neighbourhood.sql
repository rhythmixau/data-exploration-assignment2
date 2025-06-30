with neighbourhoods AS (
    select distinct neighbourhood, neighbourhood_group
    from {{ ref('bronze_listings') }}
)
select neighbourhood,
       neighbourhood_group
from neighbourhoods