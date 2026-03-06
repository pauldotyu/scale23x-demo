output "rg_name" {
  value = azurerm_resource_group.example.name
}

output "dns_zone_name" {
  value = azurerm_dns_zone.example.name
}

output "dns_zone_nameservers" {
  value = azurerm_dns_zone.example.name_servers
}

output "aks_name" {
  value = azurerm_kubernetes_cluster.example.name
}

output "argocd_app_tenant_id" {
  description = "The Tenant ID of the Azure AD Application"
  value       = data.azuread_client_config.current.tenant_id
}

output "argocd_app_client_id" {
  description = "The Application (client) ID of the Azure AD Application"
  value       = azuread_application.example.client_id
}

output "argocd_admin_object_id" {
  description = "The Object ID of user with admin access to ArgoCD"
  value       = data.azuread_client_config.current.object_id
}

output "cert_manager_identity_name" {
  description = "The Name of the User Assigned Identity for cert-manager"
  value       = azurerm_user_assigned_identity.cert_manager.name
}

output "cert_manager_client_id" {
  description = "The Client ID of the User Assigned Identity for cert-manager"
  value       = azurerm_user_assigned_identity.cert_manager.client_id
}

output "kaito_identity_name" {
  description = "The Name of the User Assigned Identity for Kaito"
  value       = azurerm_user_assigned_identity.kaito.name
}

output "otlp_traces_endpoint" {
  description = "The endpoint for OTLP traces ingestion in Azure Monitor"
  value       = azapi_resource.example.output.properties["OTLPTracesEndpoint"]
}

output "otlp_logs_endpoint" {
  description = "The endpoint for OTLP logs ingestion in Azure Monitor"
  value       = azapi_resource.example.output.properties["OTLPLogsEndpoint"]
}

output "otlp_metrics_endpoint" {
  description = "The endpoint for OTLP metrics ingestion in Azure Monitor"
  value       = azapi_resource.example.output.properties["OTLPMetricsEndpoint"]
}

output "key_vault_name" {
  description = "The name of the Azure Key Vault"
  value       = azurerm_key_vault.example.name
}

output "key_vault_url" {
  description = "The URL of the Azure Key Vault"
  value       = azurerm_key_vault.example.vault_uri
}

output "eso_client_id" {
  description = "The Client ID of the External Secrets Operator managed identity"
  value       = azurerm_user_assigned_identity.eso.client_id
}