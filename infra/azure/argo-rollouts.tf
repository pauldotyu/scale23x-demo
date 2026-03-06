resource "helm_release" "argo_rollouts" {
  name             = "argo-rollouts-release"
  repository       = "https://argoproj.github.io/argo-helm"
  chart            = "argo-rollouts"
  version          = var.argo_rollouts_version
  namespace        = "argo-rollouts"
  create_namespace = true
}