# Instructions to release a new version of Deploy To Azure CLI extension

The creation of a new release involves:

1. Creating a new wheel from existing code and hosting it.
1. Updating index file in Azure CLI extensions repository.
1. Updating Deploy To Azure CLI extension version in repository and releases

## Creating a new wheel from existing code and hosting it

To do this trigger a [Create Release - deploy-to-azure-cli-extension](https://dev.azure.com/deploy-to-azure-cli/deploy-to-azure-cli/_build?definitionId=2) build

This build will:

* create and upload wheel with the latest code (which can be downloaded from artifacts)
* this will also create a draft release in GitHub Repository
* calculate sha256 for the wheel (which can be found in logs)

### Manual Steps

* Publish the draft release in GitHub after making required changes in release notes

## Updating index file in Azure CLI extensions repository

Index file is present [here](https://github.com/Azure/azure-cli-extensions/blob/master/src/index.json) which needs to be updated so that new wheel is available for consumption in azure CLI
Find 'deploy-to-azure' to see where is the entry for 'deploy-to-azure' extension
Create a PR for updating, fiels in index json are self explanatory

## Create a new release branch and push to the repo

Create a new branch (release-0.x.0) from  master with the changes which have been released and push this new branch to the repo.

## Updating Deploy to Azure CLI extension version in repository and releases

Once relase is done make sure to update the version for Deploy-to-Azure CLI in [version.py](https://github.com/Azure/deploy-to-azure-cli-extension/blob/master/deploy-to-azure/azext_deploy_to_azure/version.py)
Also update build pipelines YAMLS
[Release Pipeline](./../.azure-pipelines/azure-pipelines-create-release.yml)

