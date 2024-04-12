# Restrict image registry

Restrict source registries and repositories for container images deployed to the cluster. Unauthorized container image sources can lead to supply chain attacks via targeted or accidental creation of malicious workloads.

## Use rule

In order to use this rule:

1. Adjust metavariable-regex for `$IMG` in `rules/restrict-image-registry.yaml` (highlighted below)
2. Create `configmap` via:
```bash
kubectl create configmap -n semgr8ns restrict-image-registry --from-file=rules/restrict-image-registry.yaml
kubectl label configmap -n semgr8ns restrict-image-registry semgr8s/rule=true
```

## Rule

```yaml title="rules/restrict-image-registry.yaml" hl_lines="29"
--8<-- "rules/restrict-image-registry.yaml"
```
