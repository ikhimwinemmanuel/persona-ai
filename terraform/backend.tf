
terraform {
  backend "s3" {
    bucket       = "personaai-terraform-state-036019073126"
    key          = "personaai/terraform.tfstate"
    region       = "ap-southeast-2"
    encrypt      = true
    use_lockfile = true
  }
}
