## Infrastructure

# First time init
```
gcloud config set project data-factory-new-dev
```
```
`cd infra`
```
```
terraform init --var-file="dev.tfvars" --backend-config="bucket=data-factory-test-211001-tfstorage" --backend-config="prefix=algocomponents"
```
# Plan the changes
```
terraform plan --var-file="dev.tfvars"
```
# Apply changes
```
terraform apply --var-file="dev.tfvars"
```