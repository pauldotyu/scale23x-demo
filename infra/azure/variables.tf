variable "location" {
  type        = string
  default     = "brazilsouth"
  description = "value of location"
}

variable "dns_zone_name" {
  type        = string
  default     = "aks.rocks"
  description = "DNS zone name"
}

variable "node_pool_count" {
  type        = number
  default     = 3
  description = "Number of nodes in the AKS node pool"
}
variable "kaito_gpu_provisioner_version" {
  type        = string
  default     = "0.4.1"
  description = "kaito gpu provisioner version"
}

variable "kaito_workspace_version" {
  type        = string
  default     = "0.9.0"
  description = "kaito workspace version"
}

variable "deploy_kaito_ragengine" {
  type        = bool
  default     = true
  description = "whether to deploy the KAITO RAGEngine"
}

variable "kaito_ragengine_version" {
  type        = string
  default     = "0.9.0"
  description = "KAITO RAGEngine version"
}

variable "kaito_workspace_features" {
  type        = list(string)
  default     = ["gatewayAPIInferenceExtension", "enableInferenceSetController"]
  description = "List of KAITO workspace features to enable"
}

variable "argo_cd_version" {
  type        = string
  default     = "9.4.5"
  description = "Argo CD Helm chart version"
}

variable "argo_workflows_version" {
  type        = string
  default     = "0.47.4"
  description = "Argo Workflows Helm chart version"
}

variable "argo_rollouts_version" {
  type        = string
  default     = "2.40.6"
  description = "Argo Rollouts Helm chart version"
}

variable "external_secrets_version" {
  type        = string
  default     = "2.0.1"
  description = "External Secrets Operator Helm chart version"
}

variable "hf_token" {
  type        = string
  sensitive   = true
  description = "Hugging Face API token for accessing gated models"
}

variable "github_deploy_key_enabled" {
  type        = bool
  default     = false
  description = "Whether to create an SSH deploy key for private repo access via Argo CD Helm chart installation. Set to false when repo is public."
}

variable "github_repo" {
  type        = string
  default     = "scale23x-demo"
  description = "GitHub repository name for deploy key"
}
