data "aws_caller_identity" "current" {}

resource "aws_iam_openid_connect_provider" "github" {
  url            = "https://token.actions.githubusercontent.com"
  client_id_list = ["sts.amazonaws.com"]
}

data "aws_iam_policy_document" "github_actions_trust" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type        = "Federated"
      identifiers = [aws_iam_openid_connect_provider.github.arn]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }

    # GitHub's OIDC template for this repository embeds immutable owner and
    # repository IDs. Keep the trust rule limited to that exact identity.
    condition {
      test     = "StringLike"
      variable = "token.actions.githubusercontent.com:sub"
      values   = ["repo:git-akshay-jadhav@136370234/releasepilot@1328490700:*"]
    }
  }
}

resource "aws_iam_role" "github_actions" {
  name               = "${var.cluster_name}-github-actions"
  assume_role_policy = data.aws_iam_policy_document.github_actions_trust.json
}

data "aws_iam_policy_document" "github_actions_deploy" {
  statement {
    effect    = "Allow"
    actions   = ["ecr:GetAuthorizationToken"]
    resources = ["*"]
  }

  statement {
    effect = "Allow"
    actions = [
      "ecr:BatchCheckLayerAvailability",
      "ecr:CompleteLayerUpload",
      "ecr:InitiateLayerUpload",
      "ecr:PutImage",
      "ecr:UploadLayerPart"
    ]
    resources = [aws_ecr_repository.releasepilot.arn]
  }

  statement {
    effect    = "Allow"
    actions   = ["eks:DescribeCluster"]
    resources = [module.eks.cluster_arn]
  }
}

resource "aws_iam_role_policy" "github_actions_deploy" {
  name   = "releasepilot-deploy"
  role   = aws_iam_role.github_actions.id
  policy = data.aws_iam_policy_document.github_actions_deploy.json
}

output "github_actions_role_arn" {
  description = "Set this value as the AWS_ROLE_ARN GitHub Actions secret"
  value       = aws_iam_role.github_actions.arn
}
