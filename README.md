# k8s-learning

### Introduction 

As a test task for Kubernetes learning, team has to develop two services and deploy them to the local Kubernetes instance.  

Technology stack: 
- MiniKube (Kubernetes with one node) 
- Helm (deployment management tool) 
- Docker containers 
- Python – for services 

### Polling Service: 

This service should expose endpoint for publishing any text which user wants. This text should be published to the scan service for verification and if text scan is passed and result of the verification successful this text should be stored in MySql database of pooling service.  

- Project structure 
  - Deployment (helm files, config maps and secrets) 
  - Source (service code) 
- Endpoints 
  - POST: /text
  - GET: /health
- Deployment (initialize this directory by using helm create command from CLI) 
  - Create templates for 
    - Deployment 
    - ConfigMap 
    - Service  
    - Ingress 
  - Configure liveness and readiness probs 
  - Configure resources requirements 
  - Configure ingress 

### Scan Service: 

This service should expose endpoint which accepts text and verify this text to find following words: “virus”, “hack” if one of these words is found the response should be “attention” otherwise “successful”. 

- Project structure
  - Deployment (helm files, config maps and secrets) 
  - Source (service code) 
- Endpoints 
  - POST: /scan 
  - GET: /health 
- Deployment (initialize this directory by using helm create command from CLI) 
  - Create templates for 
    - Deployment 
    - ConfigMap 
    - Service  
    - Ingress 
  - Configure liveness and readiness probs 
  - Configure resources requirements 
  - Configure ingress

### Minikube: 

- Install Minikube to the local machine 
- Install Helm to the Minikube local cluster 
- Create namespaces  
  - applications
  - observability
  - storages 
- Deploy both services to applications namespace 
- Deploy MySQL 

### Deploy ELK to the observability namespace 

- Deploy Filebeat as demonset to the nodes 
- Elastic & Kibana as pods 


## Deploy

Create namespaces

```shell script
kubectl create -f ./k8s/ns-applications-dev.json
kubectl create -f ./k8s/ns-logging-dev.json
kubectl create -f ./k8s/ns-observability-dev.json
kubectl create -f ./k8s/ns-storage-dev.json
```

```shell script
helm install credentials --namespace=applications --set mysql.username=dev-test-user -f ./k8s/common/values.yaml ./k8s/common/
```

Install Nginx Ingress

```shell script
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
helm install ingress-nginx ingress-nginx/ingress-nginx
```

Install Scanner

```shell script
helm install scanner --namespace=applications -f k8s/scanner/values.yaml k8s/scanner
```

Install MySQL

```shell script
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
helm install -n storage mysql --set auth.database=service --set auth.username=python bitnami/mysql
```


Install vector.dev

```shell script
helm repo add timberio https://packages.timber.io/helm/latest
helm repo update
helm install --namespace logging vector timberio/vector-agent --values k8s/vector-values.yaml
```

Install Elastic & Kibana

```shell script
helm repo add elastic https://Helm.elastic.co
helm repo update
helm install --namespace logging elasticsearch elastic/elasticsearch -f k8s/elastic-values.yaml 
helm install --namespace logging kibana elastic/kibana
```

Accessing Kibana

```shell script
kubectl port-forward -n logging $(kubectl get pods -n logging | grep kibana | awk '{print $1}') 5601
```

http://localhost:5601/app/home

Install Puller

```shell script
helm install puller --namespace=applications --set auth.password=$(kubectl get secret --namespace storage mysql -o jsonpath="{.data.mysql-password}" | base64 --decode) -f k8s/puller/values.yaml k8s/puller
```
