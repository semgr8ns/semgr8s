---
apiVersion: v1
kind: Namespace
metadata:
   name: __NAMESPACE__
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: __WEBHOOK__-dep
  namespace: __NAMESPACE__
  labels:
    app: __WEBHOOK__
spec:
  replicas: 2
  selector:
    matchLabels:
      app: __WEBHOOK__
  template:
    metadata:
      labels:
        app: __WEBHOOK__
    spec:
      containers:
        - name: __WEBHOOK__-container
          image: __TAG__
          imagePullPolicy: Always
          volumeMounts:
            - mountPath: /etc/ssl
              name: __WEBHOOK__-certs
              readOnly: true
          resources:
            limits:
              cpu: "100m"
              memory: "256Mi"
            requests:
              cpu: "100m"
              memory: "256Mi"
          ports:
            - containerPort: 5000
      volumes:
      - name: __WEBHOOK__-certs
        secret:
          secretName: __WEBHOOK__-secret
---
apiVersion: v1
kind: Service
metadata:
  name: __WEBHOOK__-svc
  namespace: __NAMESPACE__
spec:
  selector:
    app: __WEBHOOK__
  ports:
  - port: 443
    targetPort: 5000
