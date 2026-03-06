resource "kubernetes_manifest" "argocd_certificate" {
  manifest = provider::kubernetes::manifest_decode(
    templatefile("${path.module}/argocd-tls.tmpl",
      {
        COMMON_NAME = data.azurerm_dns_zone.example.name
      }
  ))
  depends_on = [
    kubernetes_manifest.cert_manager_clusterissuer,
  ]
}

resource "kubernetes_manifest" "argocd_gateway" {
  manifest = provider::kubernetes::manifest_decode(
    templatefile("${path.module}/argocd-gateway.tmpl",
      {
        DNS_NAME = data.azurerm_dns_zone.example.name
      }
  ))
}

resource "kubernetes_manifest" "argocd_httproute" {
  manifest = provider::kubernetes::manifest_decode(
    templatefile("${path.module}/argocd-httproute.tmpl",
      {
        DNS_NAME = data.azurerm_dns_zone.example.name
      }
  ))

  depends_on = [
    kubernetes_manifest.argocd_gateway,
  ]
}

# wait for the gateway service to get a load balancer ip
resource "time_sleep" "wait_for_gateway" {
  create_duration = "90s"

  depends_on = [
    kubernetes_manifest.argocd_gateway,
    kubernetes_manifest.argocd_httproute,
  ]
}

# # fetch the argo cd server service to get the load balancer ip
# data "kubernetes_service_v1" "argocd_gateway_istio" {
#   metadata {
#     name      = "argocd-gateway-istio"
#     namespace = "argocd"
#   }

#   depends_on = [time_sleep.wait_for_gateway]
# }

# # create a dns a record for the argo cd server
# resource "azurerm_dns_a_record" "argocd" {
#   name                = "argocd"
#   zone_name           = data.azurerm_dns_zone.example.name
#   resource_group_name = data.azurerm_resource_group.example.name
#   ttl                 = 60
#   records             = [data.kubernetes_service_v1.argocd_gateway_istio.status[0].load_balancer[0].ingress[0].ip]
# }