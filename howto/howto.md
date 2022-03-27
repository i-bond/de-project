# How to run the project

Preliminary steps
Fork the Repo
Create Service Acc, grant admin permissions (BigQuery Admin, Compute Admin, Storage Admin, Service Account User)
[Get creds](https://www.kaggle.com/docs/api) JSON from kaggle to use API methods
Add NAME, KEY to [Github Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)

1. Create Private keys, change terraform files (vars.tf)
2. Creating Infrastructure - substitute vatiables in vars.tf and run Terraform commands
```
cd de-project/terraform
terraform init
terraform plan
terraform apply -auto-approve
```
