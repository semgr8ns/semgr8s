apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingWebhookConfiguration
metadata:
  name: ngaddons-__WEBHOOK__
  namespace: __NAMESPACE__
webhooks:
  - name: ngaddons.__WEBHOOK__.webhook
    failurePolicy: Fail
    sideEffects: None
    timeoutSeconds: 30
    admissionReviewVersions: ["v1","v1beta1"]
    namespaceSelector:
      matchLabels:
        ngaddons/validation-webhooks: enabled
    rules:
      - apiGroups: ["apps", ""]
        resources:
          - "deployments"
          - "pods"
        apiVersions:
          - "*"
        operations:
          - CREATE
    clientConfig:
      service:
        name: __WEBHOOK__-svc
        namespace: __NAMESPACE__
        path: /validate/
      caBundle: __CA_BUNDLE__
