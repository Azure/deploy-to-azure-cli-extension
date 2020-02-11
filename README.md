[![Build Status](https://dev.azure.com/deploy-to-azure-cli/deploy-to-azure-cli/_apis/build/status/Azure.deploy-to-azure-cli-extension?branchName=master)](https://dev.azure.com/deploy-to-azure-cli/deploy-to-azure-cli/_build/latest?definitionId=1&branchName=master)

# Deploy to Azure using GitHub Actions
[GitHub Actions](https://help.github.com/en/actions/automating-your-workflow-with-github-actions) provides a powerful execution environment integrated into every step of your workflow enabling you to combine and customize your workflow. You can use GitHub actions to build Continous Integration (CI) and deployment (CD) pipelines that target Azure. Developers who are looking to set up their CI-CD pipelines will have to acquire the actions, fill in the required parameters and set up the secrets, to execute the workflows. How about we do all of that for you with a single command?    

The Deploy to Azure extension alleviates developer pain in building workflows that target Azure by abstracting away the configuration pain and reducing concept count.

## Installing the extension
The Deploy to Azure is distributed as an extension to [Azure CLI](https://docs.microsoft.com/cli/azure/what-is-azure-cli?view=azure-cli-latest). Follow the steps given below to install the extension.
1. [Install Azure CLI](https://docs.microsoft.com/cli/azure/install-azure-cli?view=azure-cli-latest) . You must have at least `v2.0.60`, whcih you can verify with `az --version` command.
2. Add Deploy to Azure extension by running the command  
`az extension add --name deploy-to-azure`

# Deploy to Azure Kubernetes Service
The `az aks app up` command builds the application container image, pushes the image to [Azure Container Registry](https://docs.microsoft.com/en-us/azure/container-registry/container-registry-intro), and deploys the image to an [Azure Kuberentes Service](https://docs.microsoft.com/azure/aks/intro-kubernetes) instance. Follow the steps below to get started.

1. You need to be logged in to Azure CLI. Run the `az login` command.  
If the CLI can open your default browser, it will do so and load a sign-in page. Otherwise, you need to open a browser page and follow the instructions on the command line to enter an authorization code after navigating to https://aka.ms/devicelogin in your browser. For more information, see the [Azure CLI login page](https://docs.microsoft.com/cli/azure/authenticate-azure-cli?view=azure-cli-latest).

2. Run the command `az aks app up` and provide the GitHub repository URL  
`az aks app up -r https://github.com/contoso/samplerepo`  
Alternatively, you can run the command from within the local checkout of the repository and the repository URL will be inferred from the git context. If both are available, the command parameter takes precedence.

3. Provide your GitHub credentials to generate a PAT token, which will be used to commit the configuration files. Alternatively, you can provide the PAT token directly as well.

4. The command does a repository analysis to understand the language breakdown and also detect availability of any docker files.  
If a docker file is available, the docker file in the repository is used.    
In the absence of a docker file, the command generates a docker file based on the language split and depending on whether it can infer the build mechanism with high confidence. In the absence of the latter, the command will fail. 

5. Provide the ACR and AKS instances that you want to target.

6. The command creates the required secrets in the GitHub repository.

7. The command also generates the required helm charts and the action workflow file. The following configuration files are then committed into the GitHub repository, using the token generated in step 1.
    - Docker file and dockerignore if genereated.
    - Helm Charts
    - Action workflow file

8. The workflow is created and kick started with the commit of the configuration files. You can monitor the status of the workflow run, from the CLI or use the URL provided to navigate to the GitHub workflow run view. 

# Deploy to Azure Container Instance

The `az container app up` command builds the application container image, pushes the image to an ACR and deploys the image to an [Azure Container Instance](https://docs.microsoft.com/azure/container-instances/container-instances-overview). Follow the steps below to get started.

1. You need to be logged in to Azure CLI. Run the `az login` command.  
If the CLI can open your default browser, it will do so and load a sign-in page. Otherwise, you need to open a browser page and follow the instructions on the command line to enter an authorization code after navigating to https://aka.ms/devicelogin in your browser. For more information, see the [Azure CLI login page](https://docs.microsoft.com/cli/azure/authenticate-azure-cli?view=azure-cli-latest).

2. Run the command `az container app up` and provide the GitHub repository URL  
`az container app up -r https://github.com/contoso/samplerepo`  
Alternatively, you can run the same command from within the local checkout of the repository and the repository URL will be inferred from the git context. If both are available, the command parameter takes precedence.

3. Provide your GitHub credentials to generate a PAT token, which will be used to commit the configuration files. Alternatively, you can provide the PAT token directly as well.


5. Provide the ACR instance that you want to target.

6. The command sets up the required secrets in the GitHub repository.

7. The command also generates the action workflow file. The following configuration files are then committed into the GitHub repository, using the token generated in step 1.
    - Docker file and dockerignore if genereated.
    - Action workflow file

8. The workflow is created and kick started with the commit of the configuration files. You can monitor the status of the workflow run, from the CLI or use the URL provided to navigate to the GitHub workflow run view. 

9. The deployed application URL will be printed in CLI as well as the in the action after the workflow runs successfully.

# Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.
