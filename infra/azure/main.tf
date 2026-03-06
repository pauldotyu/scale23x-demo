data "azurerm_client_config" "current" {}

resource "random_integer" "example" {
  min = 10
  max = 99
}

resource "azurerm_resource_group" "example" {
  name     = "rg-${local.random_name}"
  location = var.location
}

resource "azurerm_dns_zone" "example" {
  name                = var.dns_zone_name
  resource_group_name = azurerm_resource_group.example.name
}

resource "azurerm_kubernetes_cluster" "example" {
  resource_group_name       = azurerm_resource_group.example.name
  location                  = azurerm_resource_group.example.location
  name                      = "aks-${local.random_name}"
  dns_prefix                = "aks-${local.random_name}"
  oidc_issuer_enabled       = true
  workload_identity_enabled = true

  default_node_pool {
    name       = "default"
    node_count = var.node_pool_count
  }

  workload_autoscaler_profile {
    keda_enabled = true
  }

  identity {
    type = "SystemAssigned"
  }

  lifecycle {
    ignore_changes = [
      default_node_pool[0].upgrade_settings,
    ]
  }
}

resource "azurerm_monitor_workspace" "example" {
  resource_group_name = azurerm_resource_group.example.name
  location            = azurerm_resource_group.example.location
  name                = "metrics-${local.random_name}"
}

resource "azurerm_log_analytics_workspace" "example" {
  resource_group_name = azurerm_resource_group.example.name
  location            = azurerm_resource_group.example.location
  name                = "logs-${local.random_name}"
  sku                 = "PerGB2018"
  retention_in_days   = 30
}

resource "azapi_resource" "example" {
  type      = "Microsoft.Insights/components@2025-01-23-preview"
  name      = "otel-${local.random_name}"
  parent_id = azurerm_resource_group.example.id
  location  = azurerm_resource_group.example.location

  schema_validation_enabled = false

  body = {
    kind = "web"
    properties = {
      ApplicationId                      = "otel-${local.random_name}"
      Application_Type                   = "web"
      Flow_Type                          = "Redfield"
      Request_Source                     = "IbizaAIExtension"
      IngestionMode                      = "LogAnalytics"
      WorkspaceResourceId                = azurerm_log_analytics_workspace.example.id
      AzureMonitorWorkspaceResourceId    = azurerm_monitor_workspace.example.id
      AzureMonitorWorkspaceIngestionMode = "Enabled"
      publicNetworkAccessForIngestion    = "Enabled"
      publicNetworkAccessForQuery        = "Enabled"
    }
  }

  response_export_values = [
    "*"
  ]
}