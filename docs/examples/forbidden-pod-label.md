# Scoping to pods

Block pods with the forbidden test label. The rule serves as an example to demonstrate how to restrict a rule to a specific resource type.

## Use rule

In order to use this rule:

1. Adjust the label mapping to the target value.
2. Adjust `kind: Pod` mapping to your target resource type.
3. Create `configmap` via:
```bash
kubectl create configmap -n semgr8ns forbidden-pod-label --from-file=rules/forbidden-pod-label.yaml
kubectl label configmap -n semgr8ns forbidden-pod-label semgr8s/rule=true
```

## Rule

```yaml title="rules/forbidden-pod-label.yaml" hl_lines="7-10"
--8<-- "rules/forbidden-pod-label.yaml"
```
