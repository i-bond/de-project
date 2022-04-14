import os
import logging

from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from google.cloud import storage
from airflow.providers.google.cloud.operators.bigquery import (
    BigQueryCreateExternalTableOperator,
    BigQueryInsertJobOperator
)
from airflow.providers.google.cloud.operators.dataproc import (
    ClusterGenerator,
    DataprocCreateClusterOperator,
    DataprocSubmitJobOperator,
    DataprocSubmitPySparkJobOperator,
    DataprocUpdateClusterOperator,
    DataprocDeleteClusterOperator
)



PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
BUCKET = os.environ.get("GCP_GCS_BUCKET")
AIRFLOW_HOME = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")
KAGGLE_JSON = os.environ.get("KAGGLE_JSON")
BIGQUERY_DATASET = os.environ.get("BIGQUERY_DATASET", 'netflix_dataset_test')
REGION = os.environ.get("GCP_REGION")
ZONE = os.environ.get("GCP_ZONE")
CLUSTER = "dataproc-spark-3"


CLUSTER_GENERATOR_CONFIG = ClusterGenerator(
    project_id=PROJECT_ID,
    zone="us-east1-c",
    master_machine_type="n1-standard-2",
    master_disk_type="pd-standard",
    master_disk_size=50, #GB
    worker_machine_type="n1-standard-2",
    num_workers=2,
    worker_disk_type="pd-standard",
    worker_disk_size=50, #GB
    storage_bucket=BUCKET,
    image_version="1.5-ubuntu18", # keep this version for ANACONDA
    optional_components=["ANACONDA", "JUPYTER"],
    enable_component_gateway=True
).make()

PYSPARK_URI = "gs://de_zoomcamp_test/de_project/code/pyspark_job.py"
PYSPARK_JOB = {
    "reference": {"project_id": PROJECT_ID},
    "placement": {"cluster_name": CLUSTER},
    "pyspark_job": {"main_python_file_uri": PYSPARK_URI},
}


default_args = {
    "owner": "airflow",
    "schedule_interval": '@once',
    "start_date": days_ago(1),
    "catchup": False,
    "retries": 1,
}


with DAG(
    dag_id="dataproc_spark_dag",
    default_args=default_args,
    max_active_runs=1,
    tags=['de-project'],
) as dag:
    # enable-component-gateway DOESN'T WORK with DataprocCreateClusterOperator
    # create_cluster = DataprocCreateClusterOperator(
    #     task_id="create_dataproc_cluster",
    #     region="us-east1",
    #     cluster_config=CLUSTER_GENERATOR_CONFIG,
    #     cluster_name=CLUSTER
    # )

    # gcloud dataproc clusters describe dataproc-spark-3 --region=us-east1
    create_cluster_gcloud = BashOperator(
        task_id='create_cluster_gcloud',
        bash_command=f"gcloud auth login --cred-file=$GOOGLE_APPLICATION_CREDENTIALS --project=$GCP_PROJECT_ID && " \
                     f"gcloud dataproc clusters create {CLUSTER} " \
                     f"--project={PROJECT_ID} --region={REGION} --zone={ZONE} " \
                     f"--master-machine-type=n1-standard-2 --master-boot-disk-type=pd-standard --master-boot-disk-size=50 "
                     f"--num-workers=2 " \
                     f"--worker-machine-type=n1-standard-2 --worker-boot-disk-type=pd-standard --worker-boot-disk-size=50 " \
                     f"--image-version=1.5-ubuntu18 --bucket={BUCKET} " \
                     f"--optional-components=ANACONDA,JUPYTER --enable-component-gateway " \
                     f"--initialization-actions gs://goog-dataproc-initialization-actions-{REGION}/connectors/connectors.sh " \
                     f"--metadata bigquery-connector-version=1.2.0 " \
                     f"--metadata spark-bigquery-connector-version=0.21.0 ",
    )

    copy_script_gcs = BashOperator(
        task_id='copy_script_gcs',
        bash_command=f"gsutil cp $AIRFLOW_HOME/dags/pyspark_job.py gs://de_zoomcamp_test/de_project/code/pyspark_job.py"
    )

    # gcloud dataproc jobs submit pyspark gs://de_zoomcamp_test/de_project/code/pyspark_job.py --cluster=dataproc-spark-3 --region=us-east1
    submit_pyspark_job = DataprocSubmitJobOperator(
        task_id="submit_pyspark_job",
        job=PYSPARK_JOB,
        region=REGION,
        project_id=PROJECT_ID
    )

    delete_cluster = DataprocDeleteClusterOperator(
        task_id="delete_dataproc_cluster",
        region=REGION,
        project_id=PROJECT_ID,
        cluster_name=CLUSTER
    )

create_cluster_gcloud >> copy_script_gcs >> submit_pyspark_job >> delete_cluster



# Testing Airflow tasks
# docker exec -it de_airflow_airflow-worker_1 bash
# airflow tasks test dataproc_spark_dag create_cluster_gcloud 2022-04-01
# airflow tasks test dataproc_spark_dag copy_script_gcs 2022-04-01
# airflow tasks test dataproc_spark_dag submit_pyspark_job 2022-04-01
# airflow tasks test dataproc_spark_dag delete_dataproc_cluster 2022-04-01












