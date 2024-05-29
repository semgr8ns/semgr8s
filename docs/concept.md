# Concept

**tl;dr**

* Semgr8s is a Kubernetes admission controller
* Semgr8s directly integrates Semgrep under the hood
* Rules are validated against admission requests that are similar to Kubernetes manifests
* Admission requests might exhibit some important differences to Kubernetes manifests
* Policy logic should be implemented via Semgrep rules NOT Semgr8s configuration

## Basics

Semgr8s is a policy controller for Kubernetes.
By configuring rules, resources can be validated or even modified upon deployment to the cluster.

Technically, Semgr8s implements the [Semgrep engine](https://github.com/semgrep/semgrep) as a Kubernetes [admission controller](https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/) in order to audit Kubernetes resources based on Semgrep-syntax rules.
Rules are either provided as local resources via configmaps or reference to a remote Semgrep registry.

Since admission requests resemble Kubernetes manifests and are converted by Semgr8s to compatible *yaml* format, custom rules can be developed based on knowledge about Kubernetes configuration and for example [Semgrep's Kubernetes rules](https://semgrep.dev/p/kubernetes) can be applied.
It is, however, important to bear [some differences in mind](#admission-requests).

Operationally, user changes to Kubernetes are applied via the Kube API that in turn exhibits [admission phases](https://kubernetes.io/blog/2019/03/21/a-guide-to-kubernetes-admission-controllers/).
During admission Kubernetes sends change requests to admission controllers via webhooks.
Semgr8s receives these so-called admission requests, validates them against preconfigured rules and returns the outcome: Admit, modify, or deny.
Accordingly, the Kube API then either persists the (modified) requests to etcd for application or stops deployment.

## Architecture & Design

![](assets/semgr8s-architecture.png#gh-light-mode-only){data-gallery="light"}![](assets/semgr8s-architecture-dark.png#gh-dark-mode-only){data-gallery="dark"}

Semgr8s is developed for installation via [helm](https://helm.sh/) to setup the required Kubernetes resources.
However, rendering of Kubernetes manifests for usage with `kubectl apply` is expected to work as well.

Configuration is maintained within `values.yaml` and kept at a minimum to maintain policy logic within rules (see [philosophy](#philosophy)).

??? abstract "`values.yaml` chart"

    ```yaml title="charts/semgr8s/values.yaml"
    --8<-- "charts/semgr8s/values.yaml"
    ```

With exception of the admission webhook, all Semgr8s resources reside in its namespace `semgr8ns`.
Semgr8s exhibits a validating and an optional mutating admission webhook for use with the [autofix](./usage.md/#autofix) feature.

??? abstract "`webhook.yaml` chart"

    ```yaml title="charts/semgr8s/templates/webhook.yaml"
    --8<-- "charts/semgr8s/templates/webhook.yaml"
    ```
Their default configuration includes all `CREATE` and `UPDATE` requests for all *apiGroups*, *resources*, and *apiVersions* for namespaces with label `semgr8s/validation=enabled`. However, `Event` resources are manually dropped in application logic to suppress unnecessary load.
The corresponding `/validate/` and `/mutate/` webhooks are exposed via HTTPS as a service that also handles load balancing.

??? abstract "`service.yaml` chart"

    ```yaml title="charts/semgr8s/templates/service.yaml"
    --8<-- "charts/semgr8s/templates/service.yaml"
    ```

The application logic is written in Python, exposed via [cheroot](https://github.com/cherrypy/cheroot) webserver for performance, using [flask](https://github.com/pallets/flask/) framework for simplicity and maintainability, packaged in a minimal container image based on [Alpine](https://hub.docker.com/_/alpine) and deployed as securely configured single Pod with configurable number of replicas (default: *2*) for scalability and availability.
The core functionality of rule validation against admission requests is implemented by directly integrating [Semgrep](https://github.com/semgrep/semgrep).

The Semgr8s application logic performs the following core functions:

* validate admission requests
* mutate admission requests
* update local rules

![](assets/semgr8s-design.png#gh-light-mode-only){data-gallery="light"}![](assets/semgr8s-design-dark.png#gh-dark-mode-only){data-gallery="dark"}

Semgrep is designed to scan files and consequently Semgr8s application logic manages rules, request and results data as files.
As the container file system is configured as `readOnlyRootFilesystem`, corresponding volumes (`/app/rules/`, `/app/data`) and additional Semgrep folders (`/.semgrep/`, `/.cache`, `/tmp`) are provided via volume mounts.
Performance-critical, small-size, ephemeral folders are mounted as *tmpfs* in order to avoid race conditions and timeouts at the expense of additional memory.
The TLS certificate for HTTPS is provided as secret volume.

For **mutation** and **validation**, an incoming admission request is input validated, the admission *object* is converted to *yaml* and written to file.
Semgrep is invoked on the admission request file using rules stored under `/app/rules/`.
Additional configuration is passed as system arguments.
Semgrep writes scan results to a results file that is parsed and rendered for admission response.
After completion request and result file are deleted to maintain a constant storage size.

Semgreps periodically runs an **update** job that gets the rule configmaps, decodes them and writes them to the file system under `/app/rules/`.
The update job runs once every minute.
Thus, adding new rules, modifying existing ones, or removing them can take up to 1min to propagate.

While the local rules provided as configmaps are updated manually, Semgr8s configuration configmaps (including remote rules) are mounted as environment variables upon container creation and require a restart for updating.

Semgr8s uses a service account with `list`/`get` configmaps permission in its own namespace to get updated rule configmaps:

??? abstract "role.yaml"

    ```yaml title="charts/semgr8s/templates/role.yaml"
    --8<-- "charts/semgr8s/templates/role.yaml"
    ```


## Admission requests

It is important to note that an admission request is in essence similar to Kubernetes manifests, but not the same and those differences might matter when writing rules.
Consider a simple pod resource:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: mypod
spec:
  containers:
    - name: mycontainer
      image: nginx
```

Semgr8s extracts the `object` from the admission request and ignores additional information.
The (reduced) admission request takes the following form:

??? abstract "Admission request"
    ```yaml hl_lines="1-3 34 37-39 41"
    apiVersion: v1
    kind: Pod
    metadata:
      annotations:
        kubectl.kubernetes.io/last-applied-configuration: '{"apiVersion":"v1","kind":"Pod","metadata":{"annotations":{},"name":"mypod","namespace":"test-semgr8s"},"spec":{"containers":[{"image":"nginx","name":"mycontainer"}]}}'
      creationTimestamp: '2024-05-10T13:47:01Z'
      managedFields:
      - apiVersion: v1
        fieldsType: FieldsV1
        fieldsV1:
          f:metadata:
            f:annotations:
              .: {}
              f:kubectl.kubernetes.io/last-applied-configuration: {}
          f:spec:
            f:containers:
              k:{"name":"mycontainer"}:
                .: {}
                f:image: {}
                f:imagePullPolicy: {}
                f:name: {}
                f:resources: {}
                f:terminationMessagePath: {}
                f:terminationMessagePolicy: {}
            f:dnsPolicy: {}
            f:enableServiceLinks: {}
            f:restartPolicy: {}
            f:schedulerName: {}
            f:securityContext: {}
            f:terminationGracePeriodSeconds: {}
        manager: kubectl-client-side-apply
        operation: Update
        time: '2024-05-10T13:47:01Z'
      name: mypod
      namespace: test-semgr8s
      uid: 2d28a432-6526-4022-96fa-cb9d0ff50756
    spec:
      containers:
      - image: nginx
        imagePullPolicy: Always
        name: mycontainer
        resources: {}
        terminationMessagePath: /dev/termination-log
        terminationMessagePolicy: File
        volumeMounts:
        - mountPath: /var/run/secrets/kubernetes.io/serviceaccount
          name: kube-api-access-xrkfj
          readOnly: true
      dnsPolicy: ClusterFirst
      enableServiceLinks: true
      preemptionPolicy: PreemptLowerPriority
      priority: 0
      restartPolicy: Always
      schedulerName: default-scheduler
      securityContext: {}
      serviceAccount: default
      serviceAccountName: default
      terminationGracePeriodSeconds: 30
      tolerations:
      - effect: NoExecute
        key: node.kubernetes.io/not-ready
        operator: Exists
        tolerationSeconds: 300
      - effect: NoExecute
        key: node.kubernetes.io/unreachable
        operator: Exists
        tolerationSeconds: 300
      volumes:
      - name: kube-api-access-xrkfj
        projected:
          defaultMode: 420
          sources:
          - serviceAccountToken:
              expirationSeconds: 3607
              path: token
          - configMap:
              items:
              - key: ca.crt
                path: ca.crt
              name: kube-root-ca.crt
          - downwardAPI:
              items:
              - fieldRef:
                  apiVersion: v1
                  fieldPath: metadata.namespace
                path: namespace
    status:
      phase: Pending
      qosClass: BestEffort
    ```

While the original resource configuration is maintained, considerable additional information is added by the Kube API.
Besides metadata and status information, most specification data explicitly declares implicit defaults or cluster specifics.
With Semgr8s both, user-supplied Kubernetes manifest data and additionally added information, can be validated and mutated.

It is certainly instructive to consider Kubernetes manifests and configuration knowledge during rule development, but it is imperative to bear in mind that rules validate admission requests in the end.
Consider for example a rule that checks whether a `securityContext` is explicitly set and otherwise adds a secure configuration (see e.g. [`run-as-non-root`](https://semgrep.dev/r?q=yaml.kubernetes.security.run-as-non-root.run-as-non-root)).
Above, we observe that the Kube API adds an explicit empty `securityContext` when none is provided and as a result the above rule offers no benefit.

## Philosophy

> Implement policy logic via Semgrep rules to leverage its extensive rule syntax and maintain a single source of truth.
> Keep Semgr8s configuration at a minimum providing only basic global settings.

Some configuration options for Semgr8s are available via `charts/semgr8s/values.yaml`.
While these might allow to implement certain policies such as resource type restriction via admission webhook scoping, it is encouraged to keep these at the minimum and maintain the policy logic within rules in order to avoid unexpected conflicts.

Similarly, Semgr8s is namespaced by restriction to namespaces with label `semgr8s/validation=enabled` which is intended as a fail safe (e.g. exclude `kube-system` or `semgr8ns`) not as a part of policy.
Restricting a certain rule to a specific namespace is entirely possible within the Semgrep rule syntax.

In essence, the configuration via `charts/semgr8s/values.yaml` should be aimed at the general scope of the policy controller and not towards policy itself.
This philosophy should be kept in mind during development and usage of Semgr8s.
