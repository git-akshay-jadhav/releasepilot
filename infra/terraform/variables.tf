variable "aws_region" {
  type    = string
  default = "ap-south-1"
}

variable "cluster_name" {
  type = string
}

variable "ecr_repository" {
  type    = string
  default = "releasepilot"
}
variable "github_repository" {
  description = "GitHub owner/repository permitted to deploy through OIDC"
  type        = string
  default     = "git-akshay-jadhav/releasepilot"
}
