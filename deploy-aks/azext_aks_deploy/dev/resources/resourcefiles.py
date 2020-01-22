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


DEPLOY_TO_FUNCTIONAPP_TEMPLATE = """# Action Requires
# 1. Setup the AZURE_CREDENTIALS secrets in your GitHub Repository
# 2. Replace app_name_place_holder with your Azure function app name
# 3. Add this yaml file to your project's .github/workflows/
# 4. Push your local project to your GitHub Repository

name: Linux_Python_Workflow

on:
  push:
    branches:
    - master

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
    - name: 'Checkout GitHub Action'
      uses: actions/checkout@master

    # If you want to use publish profile credentials instead of Azure Service Principal
    # Please comment this 'Login via Azure CLI' block
    - name: 'Login via Azure CLI'
      uses: azure/login@v1
      with:
        creds: ${{ secrets.AZURE_CREDENTIALS }}

    - name: Setup Python 3.7
      uses: actions/setup-python@v1
      with:
        python-version: 3.7

    - name: 'Run pip'
      shell: bash
      run: |
        # If your function app project is not located in your repository's root
        # Please change your directory for pip in pushd
        pushd .
        python -m pip install --upgrade pip
        pip install -r requirements.txt --target=".python_packages/lib/python3.6/site-packages"
        popd

    - name: 'Run Azure Functions Action'
      uses: Azure/functions-action@v1
      id: fa
      with:
        app-name: app_name_place_holder
        # If your function app project is not located in your repository's root
        # Please consider prefixing the project path in this package parameter
        package: '.'
        # If you want to use publish profile credentials instead of Azure Service Principal
        # Please uncomment the following line
        # publish-profile: ${{ secrets.SCM_CREDENTIALS }}

    #- name: 'use the published functionapp url in upcoming steps'
    #  run: |
    #    echo "${{ steps.fa.outputs.app-url }}"

# For more information on GitHub Actions:
#   https://help.github.com/en/categories/automating-your-workflow-with-github-actions
"""
