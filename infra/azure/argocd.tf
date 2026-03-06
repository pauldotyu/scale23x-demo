data "azuread_client_config" "current" {}

data "azuread_user" "current" {
  object_id = data.azuread_client_config.current.object_id
}

data "azuread_application_published_app_ids" "well_known" {}

data "azuread_service_principal" "msgraph" {
  client_id = data.azuread_application_published_app_ids.well_known.result["MicrosoftGraph"]
}

resource "azuread_application" "example" {
  display_name                   = "app-${local.random_name}-argocd"
  owners                         = [data.azuread_client_config.current.object_id]
  sign_in_audience               = "AzureADMyOrg"
  group_membership_claims        = ["ApplicationGroup"]
  fallback_public_client_enabled = true

  web {
    redirect_uris = [
      "https://argocd.${azurerm_dns_zone.example.name}/auth/callback",
      "http://localhost:9000/auth/callback"
    ]
  }

  public_client {
    redirect_uris = [
      "http://localhost:8085/auth/callback"
    ]
  }

  required_resource_access {
    resource_app_id = "00000003-0000-0000-c000-000000000000" # Microsoft Graph

    resource_access {
      id   = local.msgraph_oauth2_permission_scope_ids["openid"]
      type = "Scope"
    }

    resource_access {
      id   = local.msgraph_oauth2_permission_scope_ids["profile"]
      type = "Scope"
    }

    resource_access {
      id   = local.msgraph_oauth2_permission_scope_ids["email"]
      type = "Scope"
    }

    resource_access {
      id   = local.msgraph_oauth2_permission_scope_ids["User.Read"]
      type = "Scope"
    }
  }

  optional_claims {
    id_token {
      name      = "groups"
      essential = true
    }
  }
}

resource "azuread_application_federated_identity_credential" "example" {
  application_id = azuread_application.example.id
  display_name   = azuread_application.example.display_name
  audiences      = ["api://AzureADTokenExchange"]
  issuer         = azurerm_kubernetes_cluster.example.oidc_issuer_url
  subject        = "system:serviceaccount:argocd:argocd-server"
}

resource "azuread_service_principal" "example" {
  client_id = azuread_application.example.client_id
}

data "azuread_group" "example" {
  display_name = "CloudNative" # Replace with your actual group name
}

resource "azuread_service_principal_delegated_permission_grant" "example" {
  service_principal_object_id          = azuread_service_principal.example.object_id
  resource_service_principal_object_id = data.azuread_service_principal.msgraph.object_id
  claim_values                         = ["openid", "profile", "email", "User.Read"]
}

resource "azuread_app_role_assignment" "example" {
  app_role_id         = "00000000-0000-0000-0000-000000000000" # Default app role
  principal_object_id = data.azuread_group.example.object_id
  resource_object_id  = azuread_service_principal.example.object_id
}

resource "helm_release" "argo_cd" {
  name             = "argo-cd"
  repository       = "https://argoproj.github.io/argo-helm"
  chart            = "argo-cd"
  version          = var.argo_cd_version
  namespace        = "argocd"
  create_namespace = true

  values = [
    templatefile("${path.module}/argocd-values.tmpl",
      {
        AZURE_DNS_ZONE_NAME  = azurerm_dns_zone.example.name
        AZURE_TENANT_ID      = data.azurerm_client_config.current.tenant_id
        ARGOCD_APP_CLIENT_ID = azuread_application.example.client_id
        ADMIN_OBJECT_ID      = data.azuread_group.example.object_id
        SSH_PRIVATE_KEY      = var.github_deploy_key_enabled ? tls_private_key.argocd[0].private_key_openssh : ""
      }
    )
  ]
}