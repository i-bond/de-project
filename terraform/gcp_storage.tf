resource "google_storage_bucket" "data_lake_bucket" {
  name          = "de_zoomcamp_test"
  location      = var.region
  force_destroy = true

  # Optional, but recommended settings:
  storage_class = "STANDARD"
  uniform_bucket_level_access = true

  versioning {
    enabled     = true
  }
}


resource "google_bigquery_dataset" "bq_dataset" {
  dataset_id = var.bq_dataset
  project    = var.project_id
  location   = var.region
}


resource "google_bigquery_dataset" "bq_dataset_dbt" {
  dataset_id = var.bq_dataset_dbt
  project    = var.project_id
  location   = var.region
}