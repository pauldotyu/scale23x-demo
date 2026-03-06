resource "helm_release" "argo_workflows" {
  name             = "argoworkflows-release"
  repository       = "https://argoproj.github.io/argo-helm"
  chart            = "argo-workflows"
  version          = var.argo_workflows_version
  namespace        = "argo"
  create_namespace = true
}