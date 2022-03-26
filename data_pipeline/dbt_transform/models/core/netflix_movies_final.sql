{{ config(materialized='table') }}


select
    title,
    year_of_release,
    cast(
      trunc(year_of_release/10)*10 as integer
    ) as decade,
    round(avg(rating), 2) as avg_rating,
    count(rating) as votes_number
from {{ ref('netflix_movies') }}
group by title, year_of_release 
