import os
import logging

from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

from google.cloud import storage
from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateExternalTableOperator
import pyarrow.csv as pv
import pyarrow.parquet as pq
from datetime import datetime
import pandas as pd
import numpy as np


PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
BUCKET = os.environ.get("GCP_GCS_BUCKET")
AIRFLOW_HOME = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")
KAGGLE_JSON=os.environ.get("KAGGLE_JSON")


def convert_to_csv(files):
    for file in files:
        file_name = file.strip(".txt")
        new_csv = open(f'{file_name}.csv', mode='w')
        with open(file) as f:
            for line in f:
                line = line.strip()
                if line.endswith(':'):
                    movie_id = line.replace(':', '')
                else:
                    row = [x for x in line.split(',')]
                    row.insert(0, movie_id)
                    new_csv.write(','.join(row))
                    new_csv.write('\n')
                    row.clear()
        print(f'Convertation complete for {file}\n')
        new_csv.close()


def convert_to_parquet(files):
    for file in files:
       file_name = file.strip(".csv")
       df = pd.read_csv(file, names=['movie_id', 'user_id', 'rating', 'date'],
                        dtype={'movie_id': np.int64, 'user_id': np.int64, 'rating': np.int64, 'date': str}, parse_dates=['date'],
       )
       df.to_parquet(f'{file_name}.parquet')


default_args = {
    "owner": "airflow",
    "schedule_interval": '@once',
    "start_date": days_ago(1),
    "catchup": False,
    "retries": 1,
}

with DAG(
    dag_id="upload_to_gcs_dag",
    default_args=default_args,
    max_active_runs=1,
    tags=['de-project'],
) as dag:
    kaggle_download = BashOperator(
        task_id="kaggle_download",  # unique
        bash_command=f"echo '{KAGGLE_JSON}' > kaggle.json && " \     
                    "mkdir ~/.kaggle && " \
                    "mv kaggle.json ~/.kaggle && " \
                    "chmod 600 ~/.kaggle/kaggle.json && " \
                    "kaggle datasets download -d netflix-inc/netflix-prize-data",
        do_xcom_push=False,
    )

    to_csv = PythonOperator(
        task_id="to_csv",
        python_callable=convert_to_csv,
        op_kwargs={
            "files": ['combined_data_1.txt', 'combined_data_2.txt', 'combined_data_3.txt', 'combined_data_4.txt'],
        },
    )

    to_parquet = PythonOperator(
        task_id="to_parquet",
        python_callable=convert_to_parquet,
        op_kwargs={
            "files": ['combined_data_1.csv', 'combined_data_2.csv', 'combined_data_3.csv', 'combined_data_4.csv'],
        },
    )

    clear_space = BashOperator(
        task_id="clear_space_netflix",
        bash_command=f"array=($(ls | grep .csv)) && for csv_file in $array; do rm $csv_file; done",
        do_xcom_push=False,
    )