# How to run the project

### Preliminary steps
* Fork the Repo  
* Create Service Acc, grant admin permissions (BigQuery Admin, Compute Admin, Storage Admin, Service Account User)  
* Get creds JSON from kaggle to use [API methods](https://www.kaggle.com/docs/api) 
* Add NAME, KEY to [Github Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)  

1. Create Private keys, change terraform files (vars.tf)
2. Creating Infrastructure - substitute vatiables in vars.tf and run Terraform commands
```
cd de-project/terraform
terraform init
terraform plan
terraform apply -auto-approve
```
This will create 6 resources and update/add HOST secret for GitHub repo  

3. Setting up VM
Connect via SSH using MobaXterm or other similar software
Install docker and docker-compose
```
sudo apt-get update
sudo apt-get install docker.io

[https://docs.docker.com/compose/install/](https://docs.docker.com/compose/install/)
```

Configure SSH connection with Github (Forked Repo)
Move config to .ssh folder as well as generated pub/private keys for auto authentication
```
ssh-keyscan github.com >> /home/ubuntu/.ssh/known_hosts
chmod 400 ~/.ssh/de_zoomcamp ~/.ssh/de_zoomcamp.pub
eval ssh-agent -s
ssh-add  ~/.ssh/de_zoomcamp
ssh -T git@github.com
```

git clone [git@github.com](mailto:git@github.com):<your_profile>/de-project.git  
Move .env and credentials with JSON to de-project/data_pipeline/de_airflow  

4. Kick up Docker containers  
Grant permissions  
```
sudo chown -R ubuntu ~/de-project
sudo usermod -a -G docker ubuntu
Log out and log back in
```
```
cd data_pipeline/de_airflow
docker-compose build --build-arg NAME=<KAGGLE_NAME>--build-arg KEY=<KAGGLE_KEY>
docker-compose up airflow-init
docker-compose up
```
5. Running DAGs  
Go to HOST:8080 and run the DAG

6.Apply transformations in bdt (all models are stored in data_pipeline/dbt_transform/models/core)
```
dbt deps
dbt run --select netflix_movies
dbt run --select netflix_movies_final
```

7. Plug in DataStudio and Play :)  






