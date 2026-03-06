resource "helm_release" "istio_base" {
  name             = "istio-base"
  repository       = "https://istio-release.storage.googleapis.com/charts"
  chart            = "base"
  version          = "1.28.3"
  namespace        = "istio-system"
  create_namespace = true
}

resource "helm_release" "istiod" {
  name             = "istiod"
  repository       = "https://istio-release.storage.googleapis.com/charts"
  chart            = "istiod"
  version          = "1.28.3"
  namespace        = "istio-system"
  create_namespace = false

  set = [
    {
      name  = "pilot.env.ENABLE_GATEWAY_API_INFERENCE_EXTENSION"
      value = "true"
    },
  ]

  depends_on = [helm_release.istio_base]
}

resource "helm_release" "body_based_router" {
  name             = "body-based-router"
  chart            = "oci://registry.k8s.io/gateway-api-inference-extension/charts/body-based-routing"
  version          = "v1.3.0"
  namespace        = "istio-system"
  create_namespace = false

  set = [
    {
      name  = "provider.name"
      value = "istio"
    }
  ]

  depends_on = [helm_release.istiod]
}

# data "http" "gateway_api_standard_install" {
#   url = "https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.4.1/standard-install.yaml"
# }

# resource "kubernetes_manifest" "gateway_api_standard_install" {
#   manifest = yamldecode(data.http.gateway_api_standard_install.body)
# }
