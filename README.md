# semgr8s

Policy controller for Kubernetes.
Admission controller to use your well-known publicly available or custom Semgrep rules to validate k8s resources before deployment to the cluster.

:hammer_and_wrench: developed by 
<a href="https://securesystems.de">
    <picture>
      <img src="docs/assets/sse-logo.svg" height="15" alt="SSE logo"/>
    </picture>
  </a>

:zap: powered by
<a href="https://semgrep.dev">
    <picture>
      <img src="docs/assets/semgrep-logo.svg" height="15" alt="Semgrep logo"/>
    </picture>
  </a>

> :warning: semgr8s is in a proof-of-concept state. Do not use in production. Breaking changes, service interruptions, and development flow adjustments are expected.

## Getting started

Getting started to validate Kubernetes resources against Semgrep rules is only a matter of minutes:

![](docs/assets/semgr8s_demo.gif)

### Requirements

- [git](https://git-scm.com/)
- [yq v4.x](https://mikefarah.gitbook.io/yq/)
- Kubernetes cluster for testing (e.g. [kind](https://kind.sigs.k8s.io/), [microk8s](https://microk8s.io/docs), or [minikube](https://minikube.sigs.k8s.io/docs/start/))
- [kubectl](https://kubernetes.io/docs/reference/kubectl/)
- [Helm](https://helm.sh/)
- *(optional)* [make](https://www.gnu.org/software/make/) (e.g. via [build-essential](https://packages.ubuntu.com/focal/build-essential))
- *(optional)* [docker](https://docs.docker.com/get-docker/)

### Configuration & Installation

Semgr8s comes preconfigured with some basic rules.
However, configuration can be adjusted to your needs:

- Central configuration is maintained in `helm/values.yaml`.
- Configuration aims to provide the most native integration of Semgrep's functionality into Kubernetes. Working knowledge of Kubernetes and the [Semgrep documentation](https://semgrep.dev/docs/) should be sufficient to understand the concepts and options being used here.
- [Remote Semgrep](https://registry.semgrep.dev/rule) rules, rulesets, [repository rules](https://github.com/returntocorp/semgrep-rules) are configured via `.application.remoteRules` in `helm/values.yaml`, e.g. set to `"r/yaml.kubernetes.security.allow-privilege-escalation.allow-privilege-escalation"` or `"p/kubernetes"`, or `"r/yaml.kubernetes"` respectively.
- [Custom Semgrep rules](https://semgrep.dev/docs/writing-rules/overview/) can placed in `helm/rules/` and will be auto-mounted into the admission controller.
- Semgrep provides online tools to [learn](https://semgrep.dev/learn) and [create](https://semgrep.dev/playground/new) custom rules.

To deploy the preconfigured admission controller simply run:

```bash
helm install semgr8s helm --create-namespace --namespace semgr8ns
```
<details>
  <summary>output</summary>
  
  ```bash
  NAME: semgr8s
  LAST DEPLOYED: Mon Apr 24 18:38:57 2023
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
  NAME                           READY   STATUS             RESTARTS   AGE
pod/semgr8s-57c8457dff-fmdfn   0/1     Running   0          3m38s

NAME                      TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)   AGE
service/semgr8s-service   ClusterIP   10.96.205.56   <none>        443/TCP   3m38s

NAME                      READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/semgr8s   0/1     1            0           3m38s

NAME                                 DESIRED   CURRENT   READY   AGE
replicaset.apps/semgr8s-57c8457dff   1         1         0       3m38s
  ```
</details>

Once the pods are in `Running` state, you have successfully installed semgr8s :rocket:

### Testing



