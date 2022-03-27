terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
      version = "~> 4.14.0"
    }
    local = {
      source = "hashicorp/local"
      version = "~> 2.1"
    }
    tls = {
      source = "hashicorp/tls"
      version = "~> 3.1"
    }
    github = {
        source  = "integrations/github"
        version = "~> 4.0"
    }
  }
}

provider "google" {
  credentials = file(var.google_creds_path)
  project = var.gcp_project
  region = var.region
  zone = "us-east1-b"
}

provider "github" {
  token = var.gh_token
}


# GCP VM
resource "google_compute_instance" "project_instance" {
  name         = "de-zoomcamp-instance-test"
  machine_type = "e2-standard-4"
  zone         = "us-east1-b"
  tags = ["project", "airflow", "zoomcamp"]

  boot_disk {
    device_name = "de-zoomcamp-instance-test"
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2004-lts"
      size = 30
      type = "pd-balanced"
    }
  }

  network_interface {
    network = "default" # enable private IP address
    access_config {} # enable public IP address
  }

  metadata = {
    ssh_key = "${var.gce_ssh_user}:${file(var.gce_ssh_pub_key_file)}"
    }

  service_account {
    # Google recommends custom service accounts that have cloud-platform scope and permissions granted via IAM Roles.
    email  = "de-zoomcamp-user@de-zoomcamp-10.iam.gserviceaccount.com" #default for de-project
    scopes = ["cloud-platform"]
  }
}


# Firewall Rules
resource "google_compute_firewall" "project_firewall" {
  name    = "de-project-rules"
  network = "default"
  source_ranges = ["0.0.0.0/0"]
  priority = 1000
  description = "Create firewall rules for Airflow and Spark"

  allow {
    protocol = "tcp"
    ports    = ["8080", "5000-8000"] #8080
  }
  source_tags = ["airflow", "spark"]
}


#Github
resource "github_actions_secret" "vm_host" {
  repository       = var.gh_repo_name
  secret_name      = "HOST"
  plaintext_value  = google_compute_instance.project_instance.network_interface.0.access_config.0.nat_ip
  depends_on = [google_compute_instance.project_instance]
}


# Outputs
output instance_public_ip {
  description = "Public IP address of the GC instance"
  value = google_compute_instance.project_instance.network_interface.0.access_config.0.nat_ip
  depends_on = [google_compute_instance.project_instance]
}