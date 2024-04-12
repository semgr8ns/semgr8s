# Template rule

Template rule demonstrating minimal syntax at the example of a forbidden test mapping.

## Use rule

!!! warning
    Not for practical use.
    Rule is only provided as a minimal example. 

In order to use this rule:

1. Create `configmap` via:
```bash
kubectl create configmap -n semgr8ns template-rule --from-file=rules/template-rule.yaml
kubectl label configmap -n semgr8ns template-rule semgr8s/rule=true
```

## Rule

```yaml title="rules/template-rule.yaml"
--8<-- "rules/template-rule.yaml"
```
