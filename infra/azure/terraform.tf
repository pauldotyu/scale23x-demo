terraform {
  required_providers {
    azapi = {
      source  = "azure/azapi"
      version = "~> 2.8.0"
    }

    azuread = {
      source  = "hashicorp/azuread"
      version = "~> 3.7.0"
    }

    azurerm = {
      source  = "hashicorp/azurerm"
      version = "=4.57.0"
    }

    helm = {
      source  = "hashicorp/helm"
      version = "=3.1.1"
    }

    random = {
      source  = "hashicorp/random"
      version = "=3.8.1"
    }

    tls = {
      source  = "hashicorp/tls"
      version = "~> 4.2.1"
    }

    github = {
      source  = "integrations/github"
      version = "~> 6.11.1"
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

provider "github" {
  owner = "pauldotyu"
}

provider "helm" {
  kubernetes = {
    host                   = azurerm_kubernetes_cluster.example.kube_config.0.host
    username               = azurerm_kubernetes_cluster.example.kube_config.0.username
    password               = azurerm_kubernetes_cluster.example.kube_config.0.password
    client_certificate     = base64decode(azurerm_kubernetes_cluster.example.kube_config.0.client_certificate)
    client_key             = base64decode(azurerm_kubernetes_cluster.example.kube_config.0.client_key)
    cluster_ca_certificate = base64decode(azurerm_kubernetes_cluster.example.kube_config.0.cluster_ca_certificate)
  }
}