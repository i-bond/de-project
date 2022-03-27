variable gcp_project {
  default = "dummy_var" # "de-zoomcamp-10"
  type = string
  description = "Project Name"
}

variable abs_creds_path {
  default = "dummy_var"
  type = string
  description = "Project Name"
}

variable google_creds_path {
  default = "dummy_var"
  type = string
}


# SSH Keys
variable gce_ssh_pub_key_file {
  default = "dummy_var"
  type = string
}

variable gce_ssh_user {
  default = "dummy_var"
  type = string
}

variable project_id {
  default = "dummy_var"
  type = string
  description = "GCP project ID"
}

variable region {
  default = "dummy_var"
  type = string
  description = "Project region/location"
}

variable "bq_dataset" {
  description = "BigQuery Dataset that raw data (from GCS) will be written to"
  type = string
  default = "dummy_var"
}

variable "bq_dataset_dbt" {
  description = "BigQuery Dataset that raw data (from GCS) will be written to"
  type = string
  default = "dummy_var"
}


variable gh_token {
  default = "dummy_var"
  type = string
  description = "Github token"
}

variable gh_repo_name {
  default = "dummy_var"
  type = string
  description = "Github Repo Name"
}