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


DEPLOY_TO_ACI_TEMPLATE = """name: CI
on: [push, pull_request]

jobs:
    build-and-deploy:
        runs-on: ubuntu-latest
        steps:
        - name: 'Checkout GitHub Action'
          uses: actions/checkout@master

        - name: 'Login via Azure CLI'
          uses: Azure/docker-login@v1
          with:
              login-server: container_registry_name_place_holder.azurecr.io
              username: ${{ SECRETS.REGISTRY_USERNAME }}
              password: ${{ SECRETS.REGISTRY_PASSWORD }}

        - run: |
            docker build . -t container_registry_name_place_holder.azurecr.io/app_name_place_holder:${{ github.sha }}
            docker push container_registry_name_place_holder.azurecr.io/app_name_place_holder:${{ github.sha }}

        - name: 'Azure Login'
          uses: azure/login@v1
          with:
            creds: ${{ SECRETS.AZURE_CREDENTIALS }}

        - name: 'Deploy to Azure Container Instances'
          uses: azure/aci-deploy-action@v1
          with:
            resource-group resource_name_place_holder
            name: app_name_place_holder
            image: container_registry_name_place_holder.azurecr.io/app_name_place_holder:${{ github.sha }}
            ports: 80 port_number_place_holder
            dns-name-label: app_name_place_holder
            registry-login-server: container_registry_name_place_holder.azurecr.io
            registry-username: ${{ SECRETS.REGISTRY_USERNAME }}
            registry-password: ${{ SECRETS>REGISTRY_PASSWORD }}
            location: location_place_holder


        - name: 'Deploy to Azure Container Instances'
          uses: azure/CLI@v1
          with:
            azcliversion: 2.0.77
            inlineScript: |
              az container create --resource-group resource_name_place_holder --name app_name_place_holder --image container_registry_name_place_holder.azurecr.io/app_name_place_holder:${{ github.sha }} --ports 80 port_number_place_holder --dns-name-label app_name_place_holder --registry-username ${{ SECRETS.REGISTRY_USERNAME }} --registry-password ${{ SECRETS.REGISTRY_PASSWORD }}
"""


DEPLOY_TO_FUNCTIONAPP_PYTHON_LINUX_TEMPLATE = """name: Linux_Python_FunctionApp_CI
on: [push, pull_request]

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


DEPLOY_TO_FUNCTIONAPP_NODE_WINDOWS_TEMPLATE = """name: Windows_Node_FunctionApp_CI
on: [push, pull_request]

jobs:
  build-and-deploy:
    runs-on: windows-latest
    steps:
    - name: 'Checkout GitHub Action'
      uses: actions/checkout@master

    # If you want to use publish profile credentials instead of Azure Service Principal
    # Please comment this 'Login via Azure CLI' block
    - name: 'Login via Azure CLI'
      uses: azure/login@v1
      with:
        creds: ${{ secrets.AZURE_CREDENTIALS }}

    - name: Setup Node 10.x
      uses: actions/setup-node@v1
      with:
        node-version: '10.x'

    - name: 'Run npm'
      shell: pwsh
      run: |
        # If your function app project is not located in your repository's root
        # Please change your directory for npm in pushd
        pushd .
        npm install
        npm run build --if-present
        npm run test --if-present
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


DEPLOY_TO_FUNCTIONAPP_NODE_LINUX_TEMPLATE = """name: Linux_Node_FunctionApp_CI
on: [push, pull_request]

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

    - name: Setup Node 10.x
      uses: actions/setup-node@v1
      with:
        node-version: '10.x'

    - name: 'Run npm'
      shell: bash
      run: |
        # If your function app project is not located in your repository's root
        # Please change your directory for npm in pushd
        pushd .
        npm install
        npm run build --if-present
        npm run test --if-present
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


DEPLOY_TO_FUNCTIONAPP_POWERSHELL_WINDOWS_TEMPLATE = """name: Windows_PowerShell_FunctionApp_CI
on: [push, pull_request]

jobs:
  build-and-deploy:
    runs-on: windows-latest
    steps:
    - name: 'Checkout GitHub Action'
      uses: actions/checkout@master

    # If you want to use publish profile credentials instead of Azure Service Principal
    # Please comment this 'Login via Azure CLI' block
    - name: 'Login via Azure CLI'
      uses: azure/login@v1
      with:
        creds: ${{ secrets.AZURE_CREDENTIALS }}

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


DEPLOY_TO_FUNCTIONAPP_JAVA_WINDOWS_TEMPLATE = """name: Windows_Java_FunctionApp_CI

on: [push, pull_request]

jobs:
  build-and-deploy:
    runs-on: windows-latest
    steps:
    - name: 'Checkout GitHub Action'
      uses: actions/checkout@master

    # If you want to use publish profile credentials instead of Azure Service Principal
    # Please comment this 'Login via Azure CLI' block
    - name: 'Login via Azure CLI'
      uses: azure/login@v1
      with:
        creds: ${{ secrets.AZURE_CREDENTIALS }}

    - name: Setup Java 1.8.x
      uses: actions/setup-java@v1
      with:
        # If your pom.xml <maven.compiler.source> version is not in 1.8.x
        # Please change the Java version to match the version in pom.xml <maven.compiler.source>
        java-version: '1.8.x'

    - name: 'Run mvn'
      shell: pwsh
      run: |
        # If your function app project is not located in your repository's root
        # Please change your directory for maven build in pushd
        pushd ./../artifact_id_place_holder
        mvn clean package
        mvn azure-functions:package
        popd

    - name: 'Run Azure Functions Action'
      uses: Azure/functions-action@v1
      id: fa
      with:
        app-name: app_name_place_holder
        # If your function app project is not located in your repository's root
        # Please consider prefixing the project path in this package parameter
        package: ./../artifact_id_place_holder/target/azure-functions/functionapp_name_place_holder
        # If you want to use publish profile credentials instead of Azure Service Principal
        # Please uncomment the following line
        # publish-profile: ${{ secrets.SCM_CREDENTIALS }}

    #- name: 'use the published functionapp url in upcoming steps'
    #  run: |
    #    echo "${{ steps.fa.outputs.app-url }}"

# For more information on GitHub Actions:
#   https://help.github.com/en/categories/automating-your-workflow-with-github-actions
"""


DEPLOY_TO_FUNCTIONAPP_DOTNET_WINDOWS_TEMPLATE = """name: Windows_Dotnet_FunctionApp_CI
on: [push, pull_request]

jobs:
  build-and-deploy:
    runs-on: windows-latest
    steps:
    - name: 'Checkout GitHub Action'
      uses: actions/checkout@master

    # If you want to use publish profile credentials instead of Azure Service Principal
    # Please comment this 'Login via Azure CLI' block
    - name: 'Login via Azure CLI'
      uses: azure/login@v1
      with:
        creds: ${{ secrets.AZURE_CREDENTIALS }}

    - name: Setup Dotnet 2.2.300
      uses: actions/setup-dotnet@v1
      with:
        dotnet-version: '2.2.300'

    - name: 'Run dotnet'
      shell: pwsh
      run: |
        # If your function app project is not located in your repository's root
        # Please change your directory for dotnet build in pushd
        pushd .
        dotnet build --configuration Release --output ./output
        popd

    - name: 'Run Azure Functions Action'
      uses: Azure/functions-action@v1
      id: fa
      with:
        app-name: app_name_place_holder
        # If your function app project is not located in your repository's root
        # Please consider prefixing the project path in this package parameter
        package: './output'
        # If you want to use publish profile credentials instead of Azure Service Principal
        # Please uncomment the following line
        # publish-profile: ${{ secrets.SCM_CREDENTIALS }}

    #- name: 'use the published functionapp url in upcoming steps'
    #  run: |
    #    echo "${{ steps.fa.outputs.app-url }}"

# For more information on GitHub Actions:
#   https://help.github.com/en/categories/automating-your-workflow-with-github-actions
"""


DEPLOY_TO_FUNCTIONAPP_DOTNET_LINUX_TEMPLATE = """name: Linux_Dotnet_FunctionApp_CI
on: [push, pull_request]

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

    - name: Setup Dotnet 2.2.300
      uses: actions/setup-dotnet@v1
      with:
        dotnet-version: '2.2.300'

    - name: 'Run dotnet build'
      shell: bash
      run: |
        # If your function app project is not located in your repository's root
        # Please consider using pushd to change your path
        pushd .
        dotnet build --configuration Release --output ./output
        popd

    - name: 'Run Azure Functions Action'
      uses: Azure/functions-action@v1
      id: fa
      with:
        app-name: app_name_place_holder
        # If your function app project is not located in your repository's root
        # Please consider prefixing the project path in this package parameter
        package: './output'
        # If you want to use publish profile credentials instead of Azure Service Principal
        # Please uncomment the following line
        # publish-profile: ${{ secrets.SCM_CREDENTIALS }}

    #- name: 'use the published functionapp url in upcoming steps'
    #  run: |
    #    echo "${{ steps.fa.outputs.app-url }}"

# For more information on GitHub Actions:
#   https://help.github.com/en/categories/automating-your-workflow-with-github-actions
"""
