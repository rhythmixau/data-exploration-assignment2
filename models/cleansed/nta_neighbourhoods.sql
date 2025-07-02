WITH new_neighbourhoods AS (
SELECT distinct b.neighbourhood, n.ntaname, b.neighbourhood_group
FROM {{ ref('bronze_listings') }} b
LEFT JOIN {{ ref('stg_nyc_neighbourhoods') }} n ON (TRIM(n.ntaname) = TRIM(b.neighbourhood)
  OR LIST_CONTAINS(SPLIT(TRIM(n.ntaname), '-'), TRIM(b.neighbourhood)))
  AND TRIM(n.boroname) = TRIM(b.neighbourhood_group)
),
  new_neighbourhoods2 AS (
    SELECT b.neighbourhood, n.ntaname, b.neighbourhood_group
    FROM new_neighbourhoods b
    LEFT JOIN stg_nyc_neighbourhoods n ON n.ntaname LIKE '%' || b.neighbourhood || '%'
    AND TRIM(n.boroname) = TRIM(b.neighbourhood_group)
    WHERE b.ntaname IS NULL
  ),
  new_neighbourhoods3 AS (
SELECT
  neighbourhood,
  CASE --WHEN neighbourhood = '' AND neighbourhood_group = '' THEN ''
    WHEN neighbourhood = 'Bronxdale' AND neighbourhood_group = 'Bronx' THEN 'Morris Park'
    WHEN neighbourhood = 'East Morrisania' AND neighbourhood_group = 'Bronx' THEN 'Morrisania'
    WHEN neighbourhood = 'Fieldston' AND neighbourhood_group = 'Bronx' THEN 'Riverdale-Spuyten Duyvil'
    WHEN neighbourhood = 'North Riverdale' AND neighbourhood_group = 'Bronx' THEN 'Riverdale-Spuyten Duyvil'
    WHEN neighbourhood = 'Columbia St' AND neighbourhood_group = 'Brooklyn' THEN 'Carroll Gardens-Cobble Hill-Gowanus-Red Hook'
    WHEN neighbourhood = 'Prospect-Lefferts Gardens' AND neighbourhood_group = 'Brooklyn' THEN 'Prospect Lefferts Gardens-Wingate'
    WHEN neighbourhood = 'Vinegar Hill' AND neighbourhood_group = 'Brooklyn' THEN 'Downtown Brooklyn-DUMBO-Boerum Hill'
    WHEN neighbourhood = 'Flatiron District' AND neighbourhood_group = 'Manhattan' THEN 'Chelsea-Hudson Yards'
    WHEN neighbourhood = 'Marble Hill' AND neighbourhood_group = 'Manhattan' THEN 'Riverdale-Spuyten Duyvil'
    WHEN neighbourhood = 'NoHo' AND neighbourhood_group = 'Manhattan' THEN 'West Village'
    WHEN neighbourhood = 'Nolita' AND neighbourhood_group = 'Manhattan' THEN 'SoHo-Little Italy-Hudson Square'
    WHEN neighbourhood = 'Theater District' AND neighbourhood_group = 'Manhattan' THEN 'Midtown South-Flatiron-Union Square'
    WHEN neighbourhood = 'Ditmars Steinway' AND neighbourhood_group = 'Queens' THEN 'Astoria (North)-Ditmars-Steinway'
    WHEN neighbourhood = 'Neponsit' AND neighbourhood_group = 'Queens' THEN 'Breezy Point-Belle Harbor-Rockaway Park-Broad Channel'
    WHEN neighbourhood = 'Bay Terrace, Staten Island' AND neighbourhood_group = 'Staten Island' THEN 'Great Kills-Eltingville'
    WHEN neighbourhood = 'Bull''s Head' AND neighbourhood_group = 'Staten Island' THEN 'New Springville-Willowbrook-Bulls Head-Travis'
    WHEN neighbourhood = 'Concord' AND neighbourhood_group = 'Staten Island' THEN 'Grasmere-Arrochar-South Beach-Dongan Hills'
    WHEN neighbourhood = 'Grant City' AND neighbourhood_group = 'Staten Island' THEN 'Grasmere-Arrochar-South Beach-Dongan Hills'
    WHEN neighbourhood = 'Howland Hook' AND neighbourhood_group = 'Staten Island' THEN 'Mariner''s Harbor-Arlington-Graniteville'
    WHEN neighbourhood = 'Mariners Harbor' AND neighbourhood_group = 'Staten Island' THEN 'Mariner''s Harbor-Arlington-Graniteville'
    WHEN neighbourhood = 'New Dorp Beach' AND neighbourhood_group = 'Staten Island' THEN 'New Dorp-Midland Beach'
    WHEN neighbourhood = 'Randall Manor' AND neighbourhood_group = 'Staten Island' THEN 'St. George-New Brighton'
    WHEN neighbourhood = 'West Brighton' AND neighbourhood_group = 'Staten Island' THEN 'West New Brighton-Silver Lake-Grymes Hill'
    ELSE ntaname
  END AS ntaname,
  neighbourhood_group
  FROM new_neighbourhoods2 n
  WHERE n.ntaname IS NULL
  ), combined_neighbourhoods AS (
SELECT n1.neighbourhood, n1.ntaname, n1.neighbourhood_group
  FROM new_neighbourhoods n1
  WHERE n1.ntaname IS NOT NULL
  UNION
SELECT n2.neighbourhood, n2.ntaname, n2.neighbourhood_group
  FROM new_neighbourhoods2 n2
  WHERE n2.ntaname IS NOT NULL
  UNION
SELECT neighbourhood, ntaname, neighbourhood_group
  FROM new_neighbourhoods3 n3
  WHERE n3.ntaname IS NOT NULL
  ), final_neighbourhoods AS (
SELECT *,
  ROW_NUMBER() OVER(PARTITION BY neighbourhood ORDER BY neighbourhood_group, neighbourhood, ntaname) AS row_count
  FROM combined_neighbourhoods
  ), neighbourhoods_with_row_count AS (
  SELECT neighbourhood, neighbourhood_group, COUNT(neighbourhood) total_count
  FROM final_neighbourhoods
  GROUP BY neighbourhood, neighbourhood_group
  )
SELECT f.*, r.total_count FROM final_neighbourhoods f
  JOIN neighbourhoods_with_row_count r ON r.neighbourhood = f.neighbourhood AND r.neighbourhood_group = f.neighbourhood_group
ORDER BY f.neighbourhood_group, f.neighbourhood, f.ntaname