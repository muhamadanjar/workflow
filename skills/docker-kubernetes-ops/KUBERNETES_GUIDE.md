# Kubernetes Deployment Guide

## Basic Concepts

### Pod
Smallest deployable unit. Usually contains 1 container.

### Deployment
Manages replicas of pods, handles rolling updates.

### Service
Exposes pods to network, provides DNS name.

### ConfigMap
Non-sensitive configuration.

### Secret
Sensitive data (passwords, API keys).

## Deployment YAML

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-server
  labels:
    app: api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
      - name: api
        image: myregistry.azurecr.io/myapp:v1.0
        ports:
        - containerPort: 8080
        env:
        - name: DATABASE_URL
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: database-url
        - name: API_KEY
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: api-key
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
```

## Service YAML

```yaml
apiVersion: v1
kind: Service
metadata:
  name: api-service
spec:
  type: LoadBalancer  # or ClusterIP for internal
  selector:
    app: api
  ports:
  - protocol: TCP
    port: 80          # External port
    targetPort: 8080  # Container port
```

## ConfigMap & Secret

### ConfigMap
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  database-url: "postgresql://db:5432/myapp"
  log-level: "info"
  debug: "false"
```

### Secret (from file)
```bash
kubectl create secret generic app-secrets \
  --from-literal=api-key=xxx \
  --from-file=./credentials.json
```

### Secret YAML
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
type: Opaque
stringData:
  api-key: "xxx"
  db-password: "yyy"
```

## Kubectl Commands

### Deployment Operations
```bash
# Apply manifest
kubectl apply -f deployment.yaml

# View deployments
kubectl get deployments
kubectl describe deployment api-server

# Rollout
kubectl rollout status deployment/api-server
kubectl rollout history deployment/api-server
kubectl rollout undo deployment/api-server  # Rollback

# Scale
kubectl scale deployment api-server --replicas=5
```

### Pod Operations
```bash
# View pods
kubectl get pods
kubectl logs pod-name
kubectl logs -f pod-name  # Follow logs

# Interactive shell
kubectl exec -it pod-name -- sh

# Copy files
kubectl cp pod-name:/app/file.txt ./file.txt
```

### Port Forwarding
```bash
# Access service locally
kubectl port-forward svc/api-service 8080:80
```

## Namespaces

```bash
# Create namespace
kubectl create namespace production

# Apply to namespace
kubectl apply -f deployment.yaml --namespace=production

# View resources in namespace
kubectl get pods -n production
kubectl get services -n production
```

## HPA (Horizontal Pod Autoscaler)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-server
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

## Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: api-ingress
spec:
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 80
  - host: web.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web-service
            port:
              number: 80
```

## Multi-Container Pod

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-pod
spec:
  containers:
  - name: app
    image: myapp:latest
    ports:
    - containerPort: 8080
  - name: sidecar-logger
    image: filebeat:latest
    volumeMounts:
    - name: logs
      mountPath: /var/log
  volumes:
  - name: logs
    emptyDir: {}
```

## StatefulSet (for databases)

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
  - metadata:
      name: postgres-storage
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 10Gi
```
