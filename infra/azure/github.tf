resource "tls_private_key" "argocd" {
  count     = var.github_deploy_key_enabled ? 1 : 0
  algorithm = "ED25519"
}

resource "github_repository_deploy_key" "argocd" {
  count      = var.github_deploy_key_enabled ? 1 : 0
  title      = "Argo CD (${local.random_name})"
  repository = var.github_repo
  key        = tls_private_key.argocd[0].public_key_openssh
  read_only  = true
}
