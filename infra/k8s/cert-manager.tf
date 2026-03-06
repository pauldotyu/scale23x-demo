resource "kubernetes_manifest" "cert_manager_clusterissuer" {
  manifest = provider::kubernetes::manifest_decode(
    templatefile("${path.module}/cert-manager-clusterissuer.tmpl",
      {
        EMAIL               = data.azuread_user.current.mail
        RESOURCE_GROUP_NAME = data.azurerm_resource_group.example.name
        SUBSCRIPTION_ID     = data.azurerm_client_config.current.subscription_id
        HOSTED_ZONE_NAME    = data.azurerm_dns_zone.example.name
        CLIENT_ID           = data.azurerm_user_assigned_identity.cert_manager.client_id
      }
  ))
}
