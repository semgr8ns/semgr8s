![](assets/semgr8s-logo-full-dark.png#gh-dark-mode-only){ .off-glb }
![](assets/semgr8s-logo-full-light.png#gh-light-mode-only){ .off-glb }

<h2 align="center">
Semgrep-based Policy controller for Kubernetes.
</h2>
Admission controller to use your well-known publicly available or custom Semgrep rules to validate k8s resources before deployment to the cluster.

:hammer_and_wrench: developed by [![](assets/sse-logo-dark.svg#gh-dark-mode-only){ .off-glb }![](assets/sse-logo-light.svg#gh-light-mode-only){ .off-glb }](https://securesystems.de/)

:zap: powered by [![](assets/semgrep-logo-dark.svg#gh-dark-mode-only){ .off-glb }![](assets/semgrep-logo-light.svg#gh-light-mode-only){ .off-glb }](https://semgrep.dev)

> :warning: semgr8s is in a proof-of-concept state. Do not use in production. Breaking changes, service interruptions, and development flow adjustments are expected.

## Quick start

Getting started to validate Kubernetes resources against Semgrep rules is only a matter of minutes:

![](assets/semgr8s-demo.gif)

### Requirements

- [git](https://git-scm.com/)
- Kubernetes cluster for testing (e.g. [kind](https://kind.sigs.k8s.io/), [microk8s](https://microk8s.io/docs), or [minikube](https://minikube.sigs.k8s.io/docs/start/))
- [kubectl](https://kubernetes.io/docs/reference/kubectl/)
- [Helm](https://helm.sh/)

### Installation

Installation files are contained within the source code repository:

```bash
git clone https://github.com/semgr8ns/semgr8s.git
cd semgr8s
```

Semgr8s comes preconfigured with some basic rules.
However, configuration can be adjusted to your needs:

- Central configuration is maintained in `charts/semgr8s/values.yaml`.
- Configuration aims to provide the most native integration of Semgrep's functionality into Kubernetes. Working knowledge of Kubernetes and the [Semgrep documentation](https://semgrep.dev/docs/) should be sufficient to understand the concepts and options being used here.
- [Remote Semgrep](https://registry.semgrep.dev/rule) rules, rulesets, [repository rules](https://github.com/returntocorp/semgrep-rules) are configured via `.application.remoteRules` in `charts/semgr8s/values.yaml`, e.g. set to `"r/yaml.kubernetes.security.allow-privilege-escalation.allow-privilege-escalation"` or `"p/kubernetes"`, or `"r/yaml.kubernetes"` respectively.
- [Custom Semgrep rules](https://semgrep.dev/docs/writing-rules/overview/) can placed in `charts/semgr8s/rules/` and will be auto-mounted into the admission controller.
- Semgrep provides online tools to [learn](https://semgrep.dev/learn) and [create](https://semgrep.dev/playground/new) custom rules.

To deploy the preconfigured admission controller simply run:

```bash
helm install semgr8s charts/semgr8s --create-namespace --namespace semgr8ns
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
Semgr8s only validates resources in namespaces with label `semgr8s/validation=enabled`:

```bash
kubectl apply -f tests/demo/00_test-namespace.yaml
```
<details>
  <summary>output</summary>
  
  ```bash
  namespace/test-semgr8s created
  ```
</details>

It denies creating pods with non-compliant configuration according to the local rules in `charts/semgr8s/rules` and `.application.remoteRules`  `charts/semgr8s/values.yaml`:

```bash
kubectl apply -f tests/demo/40_failing-deployment.yaml
```
<details>
  <summary>output</summary>
  
  ```bash
  Error from server: error when creating "tests/demo/40_failing-deployment.yaml": admission webhook "semgr8s-svc.semgr8ns.svc" denied the request: Found 1 violation(s) of the following policies: 
  * rules.test-semgr8s-forbidden-label
  Error from server: error when creating "tests/demo/40_failing-deployment.yaml": admission webhook "semgr8s-svc.semgr8ns.svc" denied the request: Found 1 violation(s) of the following policies: 
  * yaml.kubernetes.security.writable-filesystem-container.writable-filesystem-container
  Error from server: error when creating "tests/demo/40_failing-deployment.yaml": admission webhook "semgr8s-svc.semgr8ns.svc" denied the request: Found 1 violation(s) of the following policies: 
  * yaml.kubernetes.security.privileged-container.privileged-container
  Error from server: error when creating "tests/demo/40_failing-deployment.yaml": admission webhook "semgr8s-svc.semgr8ns.svc" denied the request: Found 1 violation(s) of the following policies: 
  * yaml.kubernetes.security.hostnetwork-pod.hostnetwork-pod
  ```
</details>

Compliantly configured resources on the other hand are permitted to the cluster:

```bash
kubectl apply -f tests/demo/20_passing-deployment.yaml
```
<details>
  <summary>output</summary>
  
  ```bash
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
  namespace "test-semgr8s" deleted
  pod "passing-testpod-1" deleted
  Error from server (NotFound): error when deleting "tests/demo/40_failing-deployment.yaml": pods "forbiddenlabel-pod" not found
  Error from server (NotFound): error when deleting "tests/demo/40_failing-deployment.yaml": pods "failing-testpod-1" not found
  Error from server (NotFound): error when deleting "tests/demo/40_failing-deployment.yaml": pods "failing-testpod-2" not found
  Error from server (NotFound): error when deleting "tests/demo/40_failing-deployment.yaml": pods "failing-testpod-3" not found

  ```
</details>

## Next steps

Excited about Semgr8s? Here is some next steps:

* :books: For more details, checkout the [Concept](https://semgr8ns.github.io/semgr8s/latest/concept/) or [Usage](https://semgr8ns.github.io/semgr8s/latest/usage/)
* :writing_hand: To share feedback, reach out via [GitHub Discussions](https://github.com/semgr8ns/semgr8s/discussions)
* :bug: Report bugs via [GitHub Issues](https://github.com/semgr8ns/semgr8s/issues)

## Management

### Compatibility

Semgr8s is expected to be compatible with most common Kubernetes services.
It supports all maintained Kubernets versions and is actively tested against versions v1.20 and higher.

In case you identify any incompatibilities, please [create an issue](https://github.com/semgr8ns/semgr8s/issues/new/choose) :hearts:

### Versions

The latest stable version of Semgr8s is available on the [`main`](https://github.com/semgr8ns/semgr8s) branch.
[Releases](https://github.com/semgr8ns/semgr8s/tags) follow [semantic versioning](https://semver.org/) standards to facilitate compatibility.
For each release, a signed container image tagged with the version is published in the [Semgr8s GitHub Container Registry](https://github.com/semgr8ns/semgr8s/pkgs/container/semgr8s) (GHCR).
Latest developments are available on the [`dev`](https://github.com/semgr8ns/semgr8s/tree/dev) branch, but should be considered unstable and a pre-built container image is provided with `dev` tag.

### Artifacts

Semgr8s employs an automated build pipeline that publishes artifacts to GHCR.
Container images are available via:

```bash
docker pull ghcr.io/semgr8ns/semgr8s:main # (1)!
```

1.  Use your tag of interest, e.g. `v0.1.16`.

Images are signed using keyless sigstore [OIDC signatures](https://docs.sigstore.dev/verifying/verify/#keyless-verification-using-openid-connect) including provenance and SBOM data:


```bash
cosign tree ghcr.io/semgr8ns/semgr8s:main # (1)!
```

1.  Use your tag of interest, e.g. `v0.1.16`.

<details>
  <summary>output</summary>
  
  ```bash
  📦 Supply Chain Security Related artifacts for an image: ghcr.io/semgr8ns/semgr8s:main
  └── 💾 Attestations for an image tag: ghcr.io/semgr8ns/semgr8s:sha256-e372107c1856ab76f44658e263c30a8ab5afe296c95ded498afde9596d1c9e12.att
    └── 🍒 sha256:1d3677b036cfeb233aed550029a689468a0ceb6c9c495315fbb789f6f386b627
  └── 🔐 Signatures for an image tag: ghcr.io/semgr8ns/semgr8s:sha256-e372107c1856ab76f44658e263c30a8ab5afe296c95ded498afde9596d1c9e12.sig
    └── 🍒 sha256:3eea0c4186f4a88658bee01dbff07bcc9f4605fadfcb7a02a9387ad223c7d23e

  ```
</details>

Verify via signatures via:

```bash hl_lines="5"
cosign verify \
    --certificate-oidc-issuer 'https://token.actions.githubusercontent.com' \
    --certificate-identity-regexp '^https://github\.com/semgr8ns/semgr8s/' \
    --certificate-github-workflow-repository 'semgr8ns/semgr8s' \
    ghcr.io/semgr8ns/semgr8s:main # (1)!
```

1.  Use your tag of interest, e.g. `v0.1.16`.

Download verified SBOM in `cyclonedx-json` format:

```bash hl_lines="5"
cosign verify-attestation --type cyclonedx \
    --certificate-oidc-issuer 'https://token.actions.githubusercontent.com' \
    --certificate-identity-regexp '^https://github\.com/semgr8ns/semgr8s/' \
    --certificate-github-workflow-repository 'semgr8ns/semgr8s' \
    ghcr.io/semgr8ns/semgr8s:main | # (1)!
    jq -r '.payload' | base64 -d | jq '.predicate' \
    > sbom.cdx
```

1.  Use your tag of interest, e.g. `v0.1.16`.

Helm charts themselves are shared via the [GitHub repository](https://github.com/semgr8ns/semgr8s/tree/main/charts/semgr8s).

### Development

Semgr8s is *open source* and *open development*.
We aim to announce major developments via [GitHub Discussions](https://github.com/semgr8ns/semgr8s/discussions/categories/announcements).
Information on responsible disclosure of vulnerabilities and tracking of past findings is available in the [Security Policy](./SECURITY.md).
Bug reports should be filed as [GitHub issues](https://github.com/semgr8ns/semgr8s/issues/new) to share status and potential fixes with other users.
Contributions should be provided as pull requests against the `dev` branch.

We hope to get as many direct contributions and insights from the community as possible to steer further development :rocket:

## Wall of fame

Thanks to all the fine people directly contributing commits/PRs to Semgr8s:

<a href="https://github.com/semgr8ns/semgr8s/graphs/contributors">
  <img src="https://contributors-img.web.app/image?repo=semgr8ns/semgr8s" />
</a>

Big shout-out also to all who support the project via issues, discussions and feature requests :pray:

## Resources

Several Semgr8s resources are available:

- [:octicons-mark-github-16: Semgr8s repository](https://github.com/semgr8ns/semgr8s)
- [:fontawesome-solid-box: Semgr8s container registry](https://github.com/semgr8ns/semgr8s/pkgs/container/semgr8s)
- [:fontawesome-solid-book: Semgr8s documentation](https://semgr8ns.github.io/semgr8s/latest/)
- [:fontawesome-solid-message: Semgr8s discussions](https://github.com/semgr8ns/semgr8s/discussions)
