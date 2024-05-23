# Template autofix rule

Template rule demonstrating minimal syntax for [autofix rules](../usage.md#autofix) at the example of a forbidden test mapping that is removed upon fixing.

## Use rule

!!! warning
    Not for practical use.
    Rule is only provided as a minimal example. 

In order to use this rule:

1. Create `configmap` via:
```bash
kubectl create configmap -n semgr8ns template-autofix-rule --from-file=rules/template-autofix-rule.yaml
kubectl label configmap -n semgr8ns template-autofix-rule semgr8s/rule=true
```

## Rule

```yaml title="rules/template-autofix-rule.yaml"
--8<-- "rules/template-autofix-rule.yaml"
```
