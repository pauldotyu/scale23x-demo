terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "=4.58.0"
    }

    random = {
      source  = "hashicorp/random"
      version = "=3.8.1"
    }

    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "=3.0.1"
    }

    time = {
      source  = "hashicorp/time"
      version = "=0.13.1"
    }
  }
}

provider "azurerm" {
  features {
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
  }
}

provider "kubernetes" {
  host                   = data.azurerm_kubernetes_cluster.example.kube_config.0.host
  username               = data.azurerm_kubernetes_cluster.example.kube_config.0.username
  password               = data.azurerm_kubernetes_cluster.example.kube_config.0.password
  client_certificate     = base64decode(data.azurerm_kubernetes_cluster.example.kube_config.0.client_certificate)
  client_key             = base64decode(data.azurerm_kubernetes_cluster.example.kube_config.0.client_key)
  cluster_ca_certificate = base64decode(data.azurerm_kubernetes_cluster.example.kube_config.0.cluster_ca_certificate)
}
