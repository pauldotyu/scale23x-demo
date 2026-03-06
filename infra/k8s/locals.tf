data "terraform_remote_state" "azure" {
  backend = "local"

  config = {
    path = "../azure/terraform.tfstate"
  }
}

locals {
  azure = data.terraform_remote_state.azure.outputs
}