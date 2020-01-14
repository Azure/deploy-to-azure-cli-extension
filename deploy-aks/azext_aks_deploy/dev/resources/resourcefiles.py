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

    - uses: azure/k8s-bake@v1
      with:
        renderEngine: 'helm2'
        helmChart: './charts/'
        releaseName: release_name_place_holder
      id: bake

    - uses: Azure/k8s-deploy@v1
      with:
        manifests: ${{ steps.bake.outputs.manifestsBundle }}
        images: |
          container_registry_name_place_holder.azurecr.io/app_name_place_holder:${{ github.sha }}
        imagepullsecrets: |
          demo-k8s-secret"""
