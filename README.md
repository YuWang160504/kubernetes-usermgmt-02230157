
# Kubernetes User Management Application

Student ID: 02230157

## Overview

A containerized user management application deployed on
Kubernetes using Minikube.

Features:
- Flask REST API for user CRUD operations
- PostgreSQL StatefulSet with persistent storage
- Frontend using Nginx
- Traefik Ingress routing
- Horizontal Pod Autoscaler for the API
- Vertical Pod Autoscaler recommendations for PostgreSQL

## Prerequisites

- Docker Desktop
- Minikube
- kubectl
- Git
- Windows PowerShell
- VPA controller components installed
- Kubernetes metrics-server and Traefik Ingress controller

## 1. Start Minikube

minikube start --driver=docker --cpus=2 --memory=4096

kubectl config use-context minikube

## 2. Build Container Images

From the project root:

docker build -t usermgmt-backend:v3 ./backend

docker build -t usermgmt-frontend:v1 ./frontend

minikube image load usermgmt-backend:v3

minikube image load usermgmt-frontend:v1

## 3. Configure Database Secret

Copy k8s/02-secret.example.yaml to k8s/02-secret.yaml.

Replace the example database credentials with your own
values before applying the manifest.

Do not commit k8s/02-secret.yaml.

## 4. Deploy Kubernetes Resources

kubectl apply -f k8s/01-namespace.yaml

kubectl apply -f k8s/02-secret.yaml

kubectl apply -f k8s/09-backend-configmap.yaml

kubectl apply -f k8s/03-postgres-service.yaml

kubectl apply -f k8s/04-postgres-statefulset.yaml

kubectl rollout status statefulset/postgres -n usermgmt-02230157

kubectl apply -f k8s/05-backend-deployment.yaml

kubectl apply -f k8s/06-backend-service.yaml

kubectl apply -f k8s/10-api-service.yaml

kubectl apply -f k8s/07-frontend-deployment.yaml

kubectl apply -f k8s/08-frontend-service.yaml

kubectl apply -f k8s/11-api-ingress.yaml

kubectl apply -f k8s/12-backend-hpa.yaml

kubectl apply -f k8s/13-postgres-vpa.yaml

## 5. Verify Deployment

kubectl get pods -n usermgmt-02230157

kubectl get svc -n usermgmt-02230157

kubectl get ingress -n usermgmt-02230157

kubectl get hpa -n usermgmt-02230157

kubectl describe vpa postgres-vpa -n usermgmt-02230157

## 6. Test API

kubectl port-forward -n usermgmt-02230157 svc/api 8080:80

Open another terminal:

curl.exe http://localhost:8080/users

## 7. Test Ingress

Add the following line to the Windows hosts file:

127.0.0.1 usermgmt-02230157.local

Start the Minikube tunnel in a separate terminal:

minikube tunnel

Then test:

curl.exe http://usermgmt-02230157.local/users

## 8. Test Autoscaling

Check HPA:

kubectl get hpa usermgmt-api-hpa -n usermgmt-02230157 --watch

With the tunnel running, generate load:

docker run --rm williamyeh/hey -z 3m -c 20 -host usermgmt-02230157.local http://host.docker.internal/users

Verify scale-up during the test and scale-down afterward.

## 9. Check VPA Recommendations

kubectl describe vpa postgres-vpa -n usermgmt-02230157

VPA runs in Off mode and provides recommendations
without automatically changing PostgreSQL resources.
