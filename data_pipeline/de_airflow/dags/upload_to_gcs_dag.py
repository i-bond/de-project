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
KAGGLE_JSON = os.environ.get("KAGGLE_JSON")



def convert_to_csv(path, files):
    for file in files:
        file = path + "/" + file # /opt/airflow/file
        # print(f'file_path: {file}')
        file_name = file.replace(".txt", "")
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


def convert_to_parquet(path, files):
    for file in files:
        file = path + "/" + file  # /opt/airflow/file
        file_name = file.replace(".csv", "")
        print(f"file_name: {file_name}")
        if "movie_titles" in file_name:
            df = pd.read_csv(file, sep=',', names=['movie_id', 'year_of_release', 'title'], encoding='ISO-8859-1')
            # print(df.head(5))
        else:
            # continue #skip
            df = pd.read_csv(file, names=['movie_id', 'user_id', 'rating', 'date'],
                             dtype={'movie_id': np.int64, 'user_id': np.int64, 'rating': np.int64, 'date': str}, parse_dates=['date'],
            )
        df.to_parquet(f'{file_name}.parquet')


def upload_to_gcs(path, files, bucket_name):
    """
    Ref: https://cloud.google.com/storage/docs/uploading-objects#storage-upload-object-python
    :param bucket: GCS bucket name
    :param object_name: target path & file-name
    :param local_file: source path & file-name
    :return:
    """
    for file in files:
        object_name = "de_project" + "/" + file
        file = path + "/" + file
        print(f"Uploading {object_name} to {bucket_name} from local {file}")
        # WORKAROUND to prevent timeout for files > 6 MB on 800 kbps upload speed.
        # (Ref: https://github.com/googleapis/python-storage/issues/74)
        storage.blob._MAX_MULTIPART_SIZE = 5 * 1024 * 1024  # 5 MB
        storage.blob._DEFAULT_CHUNKSIZE = 5 * 1024 * 1024  # 5 MB
        # End of Workaround

        client = storage.Client()
        bucket = client.bucket(bucket_name)

        blob = bucket.blob(object_name)
        blob.upload_from_filename(file)
        print('Dataset Uploaded!')



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
        bash_command=f"kaggle datasets download -p {AIRFLOW_HOME} --unzip -d netflix-inc/netflix-prize-data",
        do_xcom_push=False,
    )

    to_csv = PythonOperator(
        task_id="to_csv",
        python_callable=convert_to_csv,
        op_kwargs={
            "path": AIRFLOW_HOME,
            "files": ['combined_data_1.txt', 'combined_data_2.txt', 'combined_data_3.txt', 'combined_data_4.txt'],
        },
    )

    to_parquet = PythonOperator(
        task_id="to_parquet",
        python_callable=convert_to_parquet,
        op_kwargs={
            "path": AIRFLOW_HOME,
            "files": ['combined_data_1.csv', 'combined_data_2.csv', 'combined_data_3.csv', 'combined_data_4.csv',
                      'movie_titles.csv']
        },
    )

    clear_space = BashOperator(
        task_id="clear_space_netflix",
        bash_command=f"rm {AIRFLOW_HOME}/*.csv",
        do_xcom_push=False,
    )

    load_to_gcs = PythonOperator(
                task_id=f"upload_files_netflix",
                python_callable=upload_to_gcs,
                op_kwargs={
                    "path": AIRFLOW_HOME,
                    "files": ['combined_data_1.parquet', 'combined_data_2.parquet', 'combined_data_3.parquet', 'combined_data_4.parquet', 'movie_titles.parquet'],
                    "bucket_name": BUCKET,
                }
    )



kaggle_download >> to_csv >> to_parquet >> clear_space >> load_to_gcs

# docker exec -it de_airflow_airflow-worker_1 bash
# airflow tasks test upload_to_gcs_dag kaggle_download 2022-03-01 && airflow tasks test upload_to_gcs_dag to_csv 2022-03-01
# airflow tasks test upload_to_gcs_dag to_parquet 2022-03-01 && airflow tasks test upload_to_gcs_dag clear_space_netflix 2022-03-01
# airflow tasks test upload_to_gcs_dag upload_files_netflix 2022-03-01

# docker commit <containter_id> <container_tag>


