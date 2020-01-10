# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import subprocess
import json
from knack.log import get_logger
from knack.prompting import prompt
from knack.util import CLIError
from azext_aks_deploy.dev.common.prompting import prompt_user_friendly_choice_list
from azext_aks_deploy.dev.common.const import RESOURCE_GROUP_NAME

logger = get_logger(__name__)


def get_default_subscription_info():
    """
    Returns the Id, name, tenantID and environmentName of the default subscription
    None if no default is set or no subscription is found
    """
    from azure.cli.core._profile import Profile
    profile = Profile()
    dummy_user = profile.get_current_account_user()
    subscriptions = profile.load_cached_subscriptions(False)
    for subscription in subscriptions:
        if subscription['isDefault']:
            return subscription['id'], subscription['name'], subscription['tenantId'], subscription['environmentName']
    logger.debug('Your account does not have a default Azure subscription. Please run \'az login\' to setup account.')
    return None, None, None, None


def create_resource_group(name, location):
    subscription_id, subscription_name, tenant_id, environment_name = get_default_subscription_info()
    logger.warning("Using your default Azure subscription %s for creating new resource group.", subscription_name)
    rg_create = subprocess.check_output(('az group create --name {rg_name} --location {location} -o json').format(rg_name=name,location=location), shell=True)
    rg_create_json = json.loads(rg_create)
    logger.warning("Resource group created with name %s",name)
    return rg_create_json['name']
    
def create_aks_cluster(cluster_name,resource_group):
    subscription_id, subscription_name, tenant_id, environment_name = get_default_subscription_info()
    logger.warning("Using your default Azure subscription %s for creating new AKS cluster. This may take several minutes", subscription_name)
    try:
        aks_create = subprocess.check_output(('az aks create --name {cluster_name} -g {group_name} -o json').format(cluster_name=cluster_name, group_name=resource_group), shell=True)
        aks_create_json = json.loads(aks_create)
        return aks_create_json
    except Exception as ex:
        raise CLIError(ex)
    
def create_acr(registry_name,resource_group,sku):
    subscription_id, subscription_name, tenant_id, environment_name = get_default_subscription_info()
    logger.warning("Using your default Azure subscription %s for creating new Azure Container Registry.", subscription_name)
    try:
        acr_create = subprocess.check_output(('az acr create --name {acr_name} --sku {sku} -g {group_name} -o json').format(acr_name=registry_name, sku=sku, group_name=resource_group), shell=True)
        acr_create = json.loads(acr_create)
        return acr_create
    except Exception as ex:
        raise CLIError(ex)

def get_location():
    subscription_id, subscription_name, tenant_id, environment_name = get_default_subscription_info()
    logger.warning("Using your default Azure subscription %s for fetching locations.", subscription_name)
    location_list = subprocess.check_output('az account list-locations -o json', shell=True)
    location_list = json.loads(location_list)
    if location_list:
        location_choice = 0
        location_choice_list = []
        for location in location_list:
            location_choice_list.append(location['name'])
        location_choice = prompt_user_friendly_choice_list(
            "In which location do you want to create your resources?", location_choice_list)
        return location_list[location_choice]['name']

def get_aks_details(name=None):
    subscription_id, subscription_name, tenant_id, environment_name = get_default_subscription_info()
    logger.warning("Using your default Azure subscription %s for fetching AKS clusters.", subscription_name)
    aks_list = subprocess.check_output('az aks list -o json', shell=True)
    aks_list = json.loads(aks_list)
    if aks_list:
        cluster_choice = 0
        cluster_choice_list = []
        for aks_cluster in aks_list:
            if not name:
                cluster_choice_list.append(aks_cluster['name'])
            elif name.lower() == aks_cluster['name'].lower():
                return aks_cluster
        if name is not None:
            raise CLIError('Cluster with name {} could not be found. Please check using command az aks list.'.format(name))
        cluster_choice_list.append('Create a new AKS cluster')
        cluster_details = None
        cluster_choice = prompt_user_friendly_choice_list(
            "Which kubernetes cluster do you want to target?", cluster_choice_list)
        if cluster_choice == len(cluster_choice_list)-1:
            cluster_name = prompt('Please enter name of the cluster to be created: ')
            resource_group = RESOURCE_GROUP_NAME
            if not resource_group_exists(resource_group):
                location = get_location()
                create_resource_group(resource_group,location)
            # check if cluster already exists
            for aks_cluster in aks_list:
                if cluster_name.lower() == aks_cluster['name'].lower() and aks_cluster['resourceGroup']:
                    logger.warning('AKS cluster with the same name already exists. Using the existing cluster.')
                    cluster_details = aks_cluster
            if not cluster_details:
                cluster_details = create_aks_cluster(cluster_name,resource_group)
        else:
            cluster_details = aks_list[cluster_choice]
        return cluster_details


def resource_group_exists(name):
    subscription_id, subscription_name, tenant_id, _environment_name = get_default_subscription_info()
    logger.warning("Using your default Azure subscription %s for fetching Resource groups.",
                   subscription_name)
    try:
        rg_list = subprocess.check_output('az group show -n {rg_name} -o json'.format(rg_name=name), shell=True)
        logger.warning('Resource group already exists. Using resource group: {rg_name}'.format(rg_name=name))
        return True
    except BaseException as ex:
        logger.debug(ex)
        return False

def get_acr_details(resource_group,name=None):
    subscription_id, subscription_name, tenant_id, _environment_name = get_default_subscription_info()
    logger.warning("Using your default Azure subscription %s for fetching Azure Container Registries.",
                   subscription_name)
    acr_list = subprocess.check_output('az acr list -o json', shell=True)
    acr_list = json.loads(acr_list)
    if acr_list:
        registry_choice = 0
        registry_choice_list = []
        for acr_clusters in acr_list:
            if not name:
                registry_choice_list.append(acr_clusters['name'])
            elif name.lower() == acr_clusters['name'].lower():
                return acr_clusters
        if name is not None:
            raise CLIError('Container Registry with name {} could not be found. Please check using command az acr list.'.format(name))
        registry_choice_list.append('Create a new Azure Container Registry')
        registry_choice = prompt_user_friendly_choice_list(
            "Which Azure Container Registry do you want to use?", registry_choice_list)
        acr_details = None
        if registry_choice == len(registry_choice_list)-1:
            registry_name = prompt('Please enter name of the Azure Container Registry to be created: ')
            for registry in acr_list:
                if registry_name.lower() == registry['name'].lower():
                    logger.warning('Azure Container Registry with the same name already exists. Using the existing registry.')
                    acr_details = registry
            if not acr_details:
                sku= get_sku()
                acr_details = create_acr(registry_name,resource_group,sku)
        else:
            acr_details = acr_list[registry_choice]
        return acr_details

def get_sku():
    sku_list = ['Basic','Classic', 'Premium', 'Standard']
    sku_choice = prompt_user_friendly_choice_list(
            "Select the SKU of the container registry?", sku_list)
    return sku_list[sku_choice]
    

def configure_aks_credentials(cluster_name,resource_group):
    try:
        subscription_id, subscription_name, tenant_id, environment_name = get_default_subscription_info()
        logger.warning("Using your default Azure subscription %s for getting AKS cluster credentials.", subscription_name)
        aks_creds = subprocess.check_output('az aks get-credentials -n {cluster_name} -g {group_name} -o json'.format(cluster_name=cluster_name,group_name=resource_group), shell=True)
    except Exception as ex:
        raise CLIError(ex)    