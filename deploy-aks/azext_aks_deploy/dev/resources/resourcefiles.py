DEPLOY_TO_AKS_TEMPLATE = """name: CI
on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@master
    
    - uses: Azure/docker-login@v1
      with:
        login-server: container_registry_name_place_holder.azurecr.io
        username: ${{ secrets.REGISTRY_USERNAME }}
        password: ${{ secrets.REGISTRY_PASSWORD }}
    
    - run: |
        docker build . -t container_registry_name_place_holder.azurecr.io/app_name_place_holder:${{ github.sha }}
        docker push container_registry_name_place_holder.azurecr.io/app_name_place_holder:${{ github.sha }}
      
    - name: Set Context for Azure Kubernetes Cluster using azure/aks-set-context@v1 action
      uses: azure/aks-set-context@v1
      with:
        creds: '${{ secrets.AZURE_CREDENTIALS }}'
        cluster-name: cluster_name_place_holder
        resource-group: resource_name_place_holder
        
    - uses: Azure/k8s-create-secret@v1
      with:
        container-registry-url: container_registry_name_place_holder.azurecr.io
        container-registry-username: ${{ secrets.REGISTRY_USERNAME }}
        container-registry-password: ${{ secrets.REGISTRY_PASSWORD }}
        secret-name: demo-k8s-secret

    - uses: Azure/k8s-deploy@v1
      with:
        manifests: |
          manifests/deployment.yml
          manifests/service.yml
        images: |
          container_registry_name_place_holder.azurecr.io/app_name_place_holder:${{ github.sha }}
        imagepullsecrets: |
          demo-k8s-secret"""

DEPLOYMENT_MANIFEST = """apiVersion : apps/v1beta1
kind: Deployment 
metadata: 
  name: app_name_place_holder 
spec:
  replicas: 1
  template:
    metadata:
      labels:
        app: app_name_place_holder 
    spec:
      containers:
        - name: app_name_place_holder 
          image: container_registry_name_place_holder.azurecr.io/app_name_place_holder 
          ports:
          - containerPort: port_number_place_holder"""

SERVICE_MANIFEST = """apiVersion: v1
kind: Service
metadata:
    name: app_name_place_holder
spec:
    type: LoadBalancer
    ports:
    - port: port_number_place_holder 
    selector:
        app: app_name_place_holder"""