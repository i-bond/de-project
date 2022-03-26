{{ config(materialized='table') }}

with movie_ratings as (
-- select count(*) from (
select * from {{ source('core','optimized_combined_data_1') }}
union all
select * from {{ source('core','optimized_combined_data_2') }}
union all
select * from {{ source('core','optimized_combined_data_3') }}
union all
select * from {{ source('core','optimized_combined_data_4') }}
-- )
),
movie_titles as (
    select 
    cast(year_of_release as integer) as year_of_release,
    cast(movie_id as integer) as movie_id,
    cast(title as string) as title
    from {{ source('core','external_movie_titles') }}
    where year_of_release is not null
)

select 
    movie_ratings.movie_id,
    movie_ratings.user_id,
    movie_ratings.rating,
    movie_ratings.date,
    movie_titles.year_of_release,
    movie_titles.title
from movie_ratings
inner join
movie_titles
on movie_ratings.movie_id = movie_titles.movie_id





















