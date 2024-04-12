# Scoping to multiple resource types

Block workloads with the forbidden test label. The rule serves as an example to demonstrate how to restrict a rule to a set of resource types.

## Use rule

In order to use this rule:

1. Adjust the label mapping to the target value.
2. Adjust metavariable regular expression for `$KIND` to your target resource types.
3. Create `configmap` via:
```bash
kubectl create configmap -n semgr8ns forbidden-workload-label --from-file=rules/forbidden-workload-label.yaml
kubectl label configmap -n semgr8ns forbidden-workload-label semgr8s/rule=true
```

## Rule

```yaml title="rules/forbidden-workload-label.yaml" hl_lines="7-13"
--8<-- "rules/forbidden-workload-label.yaml"
```
