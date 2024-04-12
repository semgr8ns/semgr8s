# Deny `default` namespace

Deny resources deployed to the default namespace. For granular security controls, resources should be segregated by namespace.

## Use rule

In order to use this rule:

1. Create `configmap` via:
```bash
kubectl create configmap -n semgr8ns deny-default-namespace --from-file=rules/deny-default-namespace.yaml
kubectl label configmap -n semgr8ns deny-default-namespace semgr8s/rule=true
```

## Rule

```yaml title="rules/deny-default-namespace.yaml" hl_lines="29"
--8<-- "rules/deny-default-namespace.yaml"
```
