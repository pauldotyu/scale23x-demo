data "azurerm_client_config" "current" {}

data "azuread_client_config" "current" {}

data "azuread_user" "current" {
  object_id = data.azuread_client_config.current.object_id
}

data "azurerm_resource_group" "example" {
  name = local.azure.rg_name
}

data "azurerm_dns_zone" "example" {
  name                = local.azure.dns_zone_name
  resource_group_name = data.azurerm_resource_group.example.name
}

data "azurerm_kubernetes_cluster" "example" {
  name                = local.azure.aks_name
  resource_group_name = data.azurerm_resource_group.example.name
}

data "azurerm_user_assigned_identity" "cert_manager" {
  name                = local.azure.cert_manager_identity_name
  resource_group_name = data.azurerm_resource_group.example.name
}

data "azurerm_user_assigned_identity" "kaito" {
  name                = local.azure.kaito_identity_name
  resource_group_name = data.azurerm_resource_group.example.name
}

data "azuread_application" "example" {
  client_id = local.azure.argocd_app_client_id
}