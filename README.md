![](docs/assets/semgr8s-logo-full-dark.png#gh-dark-mode-only)
![](docs/assets/semgr8s-logo-full-light.png#gh-light-mode-only)
![](assets/semgr8s-logo-full-dark.png#gh-dark-mode-only)
![](assets/semgr8s-logo-full-light.png#gh-light-mode-only)

<h2 align="center">
Semgrep-based Policy controller for Kubernetes.
</h2>

Admission controller to use your well-known publicly available or custom Semgrep rules to validate k8s resources before deployment to the cluster.

:hammer_and_wrench: developed by ![](docs/assets/sse-logo-dark.svg#gh-dark-mode-only)![](docs/assets/sse-logo-light.svg#gh-light-mode-only)![](assets/sse-logo-dark.svg#gh-dark-mode-only)![](assets/sse-logo-light.svg#gh-light-mode-only)

:zap: powered by ![](docs/assets/semgrep-logo-dark.svg#gh-dark-mode-only)![](docs/assets/semgrep-logo-light.svg#gh-light-mode-only)![](assets/semgrep-logo-dark.svg#gh-dark-mode-only)![](assets/semgrep-logo-light.svg#gh-light-mode-only)

> :warning: semgr8s is in a proof-of-concept state. Do not use in production. Breaking changes, service interruptions, and development flow adjustments are expected.

## Getting started

Getting started to validate Kubernetes resources against Semgrep rules is only a matter of minutes:

![](docs/assets/semgr8s-demo.gif)
![](assets/semgr8s-demo.gif)

### Requirements

- [git](https://git-scm.com/)
- [yq v4.x](https://mikefarah.gitbook.io/yq/)
- Kubernetes cluster for testing (e.g. [kind](https://kind.sigs.k8s.io/), [microk8s](https://microk8s.io/docs), or [minikube](https://minikube.sigs.k8s.io/docs/start/))
- [kubectl](https://kubernetes.io/docs/reference/kubectl/)
- [Helm](https://helm.sh/)
- *(optional)* [make](https://www.gnu.org/software/make/) (e.g. via [build-essential](https://packages.ubuntu.com/focal/build-essential))
- *(optional)* [docker](https://docs.docker.com/get-docker/)

### Get Code

Installation files are contained within this repository:

```bash
git clone https://github.com/sse-secure-systems/semgr8s.git
cd semgr8s
```

### Configuration & Installation

Semgr8s comes preconfigured with some basic rules.
However, configuration can be adjusted to your needs:

- Central configuration is maintained in `charts/semgr8s/values.yaml`.
- Configuration aims to provide the most native integration of Semgrep's functionality into Kubernetes. Working knowledge of Kubernetes and the [Semgrep documentation](https://semgrep.dev/docs/) should be sufficient to understand the concepts and options being used here.
- [Remote Semgrep](https://registry.semgrep.dev/rule) rules, rulesets, [repository rules](https://github.com/returntocorp/semgrep-rules) are configured via `.application.remoteRules` in `charts/semgr8s/values.yaml`, e.g. set to `"r/yaml.kubernetes.security.allow-privilege-escalation.allow-privilege-escalation"` or `"p/kubernetes"`, or `"r/yaml.kubernetes"` respectively.
- [Custom Semgrep rules](https://semgrep.dev/docs/writing-rules/overview/) can placed in `charts/semgr8s/rules/` and will be auto-mounted into the admission controller.
- Semgrep provides online tools to [learn](https://semgrep.dev/learn) and [create](https://semgrep.dev/playground/new) custom rules.

To deploy the preconfigured admission controller simply run:

```bash
helm install semgr8s helm --create-namespace --namespace semgr8ns
```
<details>
  <summary>output</summary>
  
  ```bash
  NAME: semgr8s
  LAST DEPLOYED: Tue Apr 25 00:16:04 2023
  NAMESPACE: semgr8ns
  STATUS: deployed
  REVISION: 1
  TEST SUITE: None
  NOTES:
  Successfully installed semgr8s!
  ```
</details>

You can check successful deployment of semgr8s via:

```bash
kubectl get all -n semgr8ns
```
<details>
  <summary>output</summary>
  
  ```bash
  NAME                           READY   STATUS    RESTARTS   AGE
  pod/semgr8s-665dbb8756-qhqv6   1/1     Running   0          7s

  NAME                      TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)   AGE
  service/semgr8s-service   ClusterIP   10.96.135.157   <none>        443/TCP   7s

  NAME                      READY   UP-TO-DATE   AVAILABLE   AGE
  deployment.apps/semgr8s   1/1     1            1           7s

  NAME                                 DESIRED   CURRENT   READY   AGE
  replicaset.apps/semgr8s-665dbb8756   1         1         1       7s
  ```
</details>

Once all resources are in `READY` state, you have successfully installed semgr8s :rocket:

### Testing

Several test resources are provided under `tests/demo/`.
For namespaces with label `semgr8s/validation=enabled`, Semgr8s denies creating pods with insecure configuration according to the rules in `charts/semgr8s/rules`:

```bash
kubectl create -f tests/demo/failing_deployment.yaml
```
<details>
  <summary>output</summary>
  
  ```bash
  namespace/test-semgr8s-failing created
  Error from server: error when creating "tests/demo/failing_deployment.yaml": admission webhook "semgr8s-svc.semgr8ns.svc" denied the request: Found 1 violation(s) of the following policies: 
  * rules.allow-privilege-escalation-no-securitycontext
  Error from server: error when creating "tests/demo/failing_deployment.yaml": admission webhook "semgr8s-svc.semgr8ns.svc" denied the request: Found 1 violation(s) of the following policies: 
  * rules.privileged-container
  Error from server: error when creating "tests/demo/failing_deployment.yaml": admission webhook "semgr8s-svc.semgr8ns.svc" denied the request: Found 1 violation(s) of the following policies: 
  * rules.hostnetwork-pod
  ```
</details>

Securely configured resources on the other hand are permitted to the cluster:

```bash
kubectl create -f tests/demo/passing_deployment.yaml
```
<details>
  <summary>output</summary>
  
  ```bash
  namespace/test-semgr8s-passing created
  pod/passing-testpod-1 created
  ```
</details>


### Cleanup

To remove all resources of the admission controller run:

```bash
helm uninstall semgr8s -n semgr8ns
kubectl delete ns semgr8ns
```
<details>
  <summary>output</summary>
  
  ```bash
  release "semgr8s" uninstalled
  ```
</details>

Test resources are deleted via:

```bash
kubectl delete -f tests/demo/
```
<details>
  <summary>output</summary>
  
  ```bash
  namespace "test-semgr8s-failing" deleted
  namespace "test-semgr8s-passing" deleted
  pod "passing-testpod-1" deleted
  Error from server (NotFound): error when deleting "tests/demo/failing_deployment.yaml": pods "failing-testpod-1" not found
  Error from server (NotFound): error when deleting "tests/demo/failing_deployment.yaml": pods "failing-testpod-2" not found
  Error from server (NotFound): error when deleting "tests/demo/failing_deployment.yaml": pods "failing-testpod-3" not found

  ```
</details>

