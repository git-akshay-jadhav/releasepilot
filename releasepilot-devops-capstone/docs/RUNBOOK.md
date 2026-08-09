# ReleasePilot Operational Runbook

## Useful commands

```bash
kubectl get deploy,pods,hpa -n releasepilot
kubectl describe pod <pod-name> -n releasepilot
kubectl logs deploy/releasepilot -n releasepilot --tail=100
helm history releasepilot -n releasepilot
```

## Incident: failing readiness probe

1. Confirm the condition with `kubectl get pods -n releasepilot` and inspect pod events.
2. Review recent deployment changes: `helm history releasepilot -n releasepilot`.
3. Check application logs and the Grafana error-rate/latency panels.
4. If caused by the last release, rollback: `helm rollback releasepilot <previous-revision> -n releasepilot --wait`.
5. Verify `/ready` returns HTTP 200 through the service and close the incident only after alert recovery.

## Incident: high error rate

1. Confirm the alert is sustained for five minutes; inspect the error rate by route in Grafana.
2. Compare the affected release revision with the previous stable revision.
3. Scale temporarily if capacity-related: `kubectl scale deploy/releasepilot -n releasepilot --replicas=4`.
4. Roll back if a deployment introduced the regression, then create a follow-up issue with logs and timeline.

## Safe delivery checklist

- CI is green: lint, unit tests, dependency audit, and Trivy scan.
- Terraform plan is reviewed before apply.
- Image tag is immutable (Git commit SHA), never `latest`.
- Helm uses `--atomic`, so failed rollouts automatically roll back.
- AWS resources are destroyed when the demo environment is no longer required.
