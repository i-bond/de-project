#!/usr/bin/python
# coding: utf-8

import pyspark
from pyspark.sql import SparkSession
from pyspark.conf import SparkConf
from pyspark.context import SparkContext

spark = SparkSession.builder \
    .appName('test') \
    .getOrCreate()

spark.conf.set('temporaryGcsBucket', 'de_zoomcamp_test')
spark.conf.set("spark.sql.repl.eagerEval.enabled", True)

df_ratings = spark.read.parquet('gs://de_zoomcamp_test/de_project/combined_data*.parquet')
df_ratings.registerTempTable('movie_ratings')
df_titles = spark.read.parquet('gs://de_zoomcamp_test/de_project/*titles.parquet')
df_titles.registerTempTable('movie_titles')

# print(df_titles.show(10))

df_result = spark.sql("""
WITH movies_united as (
    SELECT
      movie_ratings.movie_id,
      movie_ratings.user_id,
      movie_ratings.rating,
      movie_ratings.date,
      INT(movie_titles.year_of_release),
      movie_titles.title
    FROM
        movie_ratings
    INNER JOIN
        movie_titles
    ON movie_ratings.movie_id = movie_titles.movie_id
    WHERE movie_titles.year_of_release is NOT NULL
)

SELECT
    title,
    year_of_release,
    INT(year_of_release/10)*10 as decade,
    ROUND(avg(rating), 2) as avg_rating,
    COUNT(rating) as votes_number
FROM movies_united
GROUP BY title, year_of_release
""")



df_result.write.format('bigquery') \
    .option('table', "netflix_dbt.netflix_movies_final_pyspark") \
    .save()



