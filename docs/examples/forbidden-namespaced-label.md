# Namespaced rules

Block resources with the forbidden test label in specific namespaces. The rule serves as an example to demonstrate how to restrict a rule to namespaces.

## Use rule

In order to use this rule:

1. Adjust the label mapping to the target value.
2. Adjust metavariable regular expression for `$NS` to your target namespaces.
3. Create `configmap` via:
```bash
kubectl create configmap -n semgr8ns forbidden-namespaced-label --from-file=rules/forbidden-namespaced-label.yaml
kubectl label configmap -n semgr8ns forbidden-namespaced-label semgr8s/rule=true
```

## Rule

```yaml title="rules/forbidden-namespaced-label.yaml" hl_lines="7-14"
--8<-- "rules/forbidden-namespaced-label.yaml"
```
