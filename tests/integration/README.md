# Run integration tests

Use the cluster of your choice, e.g. [kind](https://kind.sigs.k8s.io/).
Specify which semgr8s image is to be used as environment variable, e.g.:

```bash
export IMAGE=ghcr.io/semgr8ns/semgr8s
export TAG=v0.1.0
```

Run the desired integration test via:
```bash
tests/integration/main.sh "basic"
```
