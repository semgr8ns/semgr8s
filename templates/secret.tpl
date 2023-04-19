---
apiVersion: v1
kind: Secret
metadata:
  name: __WEBHOOK__-secret
  namespace: __NAMESPACE__
data:
  ca.crt: __CRT__
  ca.key: __KEY__
