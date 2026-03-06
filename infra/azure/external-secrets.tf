resource "azurerm_key_vault" "example" {
  name                       = "kv-${local.random_name}"
  location                   = azurerm_resource_group.example.location
  resource_group_name        = azurerm_resource_group.example.name
  tenant_id                  = data.azurerm_client_config.current.tenant_id
  sku_name                   = "standard"
  rbac_authorization_enabled = true
  soft_delete_retention_days = 7
  purge_protection_enabled   = false
}

resource "azurerm_role_assignment" "kv_current_user" {
  principal_id         = data.azuread_client_config.current.object_id
  scope                = azurerm_key_vault.example.id
  role_definition_name = "Key Vault Secrets Officer"
}

resource "azurerm_user_assigned_identity" "eso" {
  resource_group_name = azurerm_resource_group.example.name
  location            = azurerm_resource_group.example.location
  name                = "external-secrets"
}

resource "azurerm_role_assignment" "eso_kv_reader" {
  principal_id                     = azurerm_user_assigned_identity.eso.principal_id
  scope                            = azurerm_key_vault.example.id
  role_definition_name             = "Key Vault Secrets User"
  skip_service_principal_aad_check = true
}

resource "azurerm_federated_identity_credential" "eso" {
  resource_group_name = azurerm_resource_group.example.name
  parent_id           = azurerm_user_assigned_identity.eso.id
  name                = "external-secrets"
  issuer              = azurerm_kubernetes_cluster.example.oidc_issuer_url
  audience            = ["api://AzureADTokenExchange"]
  subject             = "system:serviceaccount:external-secrets:external-secrets"
}

resource "azurerm_key_vault_secret" "hf_token" {
  name         = "hf-token"
  value        = var.hf_token
  key_vault_id = azurerm_key_vault.example.id

  depends_on = [azurerm_role_assignment.kv_current_user]
}

resource "helm_release" "external_secrets" {
  name             = "external-secrets"
  repository       = "https://charts.external-secrets.io"
  chart            = "external-secrets"
  version          = var.external_secrets_version
  namespace        = "external-secrets"
  create_namespace = true

  set = [
    {
      name  = "serviceAccount.annotations.azure\\.workload\\.identity/client-id"
      value = azurerm_user_assigned_identity.eso.client_id
      type  = "string"
    },
    {
      name  = "webhook.podLabels.azure\\.workload\\.identity/use"
      value = "true"
      type  = "string"
    },
    {
      name  = "certController.podLabels.azure\\.workload\\.identity/use"
      value = "true"
      type  = "string"
    },
    {
      name  = "podLabels.azure\\.workload\\.identity/use"
      value = "true"
      type  = "string"
    },
  ]
}
