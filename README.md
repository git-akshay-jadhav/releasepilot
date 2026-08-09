# ReleasePilot — DevOps Capstone

ReleasePilot is a production-style **release reliability platform**. The sample service exposes its health and performance; the DevOps platform then automatically tests, secures, deploys, scales, observes, and rolls back that service.

## What this proves

| Area | Evidence in this repository |
| --- | --- |
| Application delivery | Node.js API with health, readiness, metrics, and test endpoints |
| Containers | Multi-stage Docker build, non-root user, Docker Compose |
| CI/CD | GitHub Actions: test, lint, dependency audit, image scan, publish, Helm deploy |
| Infrastructure as code | Terraform provisions a VPC, EKS cluster, and ECR repository |
| Kubernetes | Helm chart with rolling updates, probes, autoscaling, resource limits, network policy |
| Observability | Prometheus metrics, ServiceMonitor, Grafana dashboard, alert rule |
| Security | Least-privilege runtime, image scanning, GitHub OIDC (no long-lived AWS keys in GitHub) |

## Architecture

```text
Developer push -> GitHub Actions -> test + audit + Trivy -> Amazon ECR
                                                       |
                                                   Helm deploy
                                                       |
Internet -> Ingress -> Kubernetes Service -> ReleasePilot pods (EKS) -> Prometheus -> Grafana
                                              |                         |
                                              +-------------------------+-> HPA
```

## Run locally

Prerequisites: Docker Desktop (recommended) or Node.js 20+.

```bash
docker compose up --build
curl http://localhost:3000/health
curl http://localhost:3000/metrics
```

To run without Docker: `npm install`, `npm test`, then `npm start`.

## Deploy to AWS

1. In `infra/terraform`, copy `terraform.tfvars.example` to `terraform.tfvars` and set a unique cluster name. The configuration uses Amazon EKS Kubernetes 1.36, which is currently in standard support.
2. Run `terraform init && terraform apply`, then configure kubectl with `aws eks update-kubeconfig`.
3. Install monitoring once: `helm upgrade --install monitoring prometheus-community/kube-prometheus-stack -n monitoring --create-namespace`.
4. Terraform creates a GitHub OIDC provider and a role restricted to this repository's `main` branch. Copy the `github_actions_role_arn` Terraform output into GitHub as the `AWS_ROLE_ARN` secret.
5. Set GitHub variables `AWS_REGION`, `EKS_CLUSTER_NAME`, and `ECR_REPOSITORY`.
6. Push to `main`, or use `helm upgrade --install releasepilot deploy/helm/releasepilot -n releasepilot --create-namespace --set image.repository=<ECR_URI> --set image.tag=<TAG>`.

> **Cost control:** EKS and NAT gateways incur AWS charges. Run `terraform destroy` after the demonstration.

## Demo flow

1. Show `/health`, `/ready`, and `/metrics` locally.
2. Walk through the GitHub Actions quality and security gates.
3. Show Terraform state/output for repeatable infrastructure.
4. Show `kubectl get pods,hpa` and the Helm release.
5. Open the Grafana dashboard and explain request rate, latency, and error rate.
6. Trigger `GET /ready?fail=true`; explain probes and alerting.
7. Demonstrate rollback: `helm rollback releasepilot <REVISION> -n releasepilot`.

See [docs/RUNBOOK.md](docs/RUNBOOK.md) for operations and incident steps.
