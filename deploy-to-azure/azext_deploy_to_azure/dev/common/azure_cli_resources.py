# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import subprocess
import json
from knack.log import get_logger
from knack.util import CLIError
from azext_deploy_to_azure.dev.common.prompting import prompt_user_friendly_choice_list, prompt_not_empty

logger = get_logger(__name__)


def get_default_subscription_info():
    """
    Returns the Id, name, tenantID and environmentName of the default subscription
    None if no default is set or no subscription is found
    """
    from azure.cli.core._profile import Profile
    profile = Profile()
    _dummy = profile.get_current_account_user()
    subscriptions = profile.load_cached_subscriptions(False)
    for subscription in subscriptions:
        if subscription['isDefault']:
            return subscription['id'], subscription['name'], subscription['tenantId'], subscription['environmentName']
    logger.debug('Your account does not have a default Azure subscription. Please run \'az login\' to setup account.')
    return None, None, None, None


def create_aks_cluster(cluster_name, resource_group):
    _subscription_id, subscription_name, _tenant_id, _environment_name = get_default_subscription_info()
    logger.warning('Using your default Azure subscription %s for creating new AKS cluster. '
                   'This may take several minutes', subscription_name)
    try:
        aks_create = subprocess.check_output(('az aks create --name {cluster_name} -g {group_name} -o json').format(
            cluster_name=cluster_name, group_name=resource_group), shell=True)
        aks_create_json = json.loads(aks_create)
        return aks_create_json
    except Exception as ex:
        raise CLIError(ex)


def create_acr(registry_name, resource_group, sku):
    _subscription_id, subscription_name, _tenant_id, _environment_name = get_default_subscription_info()
    logger.warning('Using your default Azure subscription %s for creating new Azure Container Registry.',
                   subscription_name)
    try:
        acr_create = subprocess.check_output(
            ('az acr create --name {acr_name} --sku {sku} -g {group_name} -o json')
            .format(acr_name=registry_name, sku=sku, group_name=resource_group), shell=True)
        acr_create = json.loads(acr_create)
        return acr_create
    except Exception as ex:
        raise CLIError(ex)


def get_resource_group():
    _subscription_id, subscription_name, _tenant_id, _environment_name = get_default_subscription_info()
    logger.warning("Using your default Azure subscription %s for fetching Resource Groups.", subscription_name)
    group_list = subprocess.check_output('az group list -o json', shell=True)
    group_list = json.loads(group_list)
    if not group_list:
        return None
    group_choice = 0
    group_choice_list = []
    for group in group_list:
        group_choice_list.append(group['name'])
    group_choice = prompt_user_friendly_choice_list(
        "In which resource group do you want to create your resources?", group_choice_list)
    return group_list[group_choice]['name']


def get_aks_details(name=None):
    _subscription_id, subscription_name, _tenant_id, _environment_name = get_default_subscription_info()
    logger.warning("Using your default Azure subscription %s for fetching AKS clusters.", subscription_name)
    aks_list = subprocess.check_output('az aks list -o json', shell=True)
    aks_list = json.loads(aks_list)
    if not aks_list:
        # Do we want to fail here??
        return None
    cluster_choice = 0
    cluster_choice_list = []
    for aks_cluster in aks_list:
        if not name:
            cluster_choice_list.append(aks_cluster['name'])
        elif name.lower() == aks_cluster['name'].lower():
            return aks_cluster
    if name is not None:
        raise CLIError('Cluster with name {} could not be found. Please check using command az aks list.'
                       .format(name))
    cluster_choice_list.append('Create a new AKS cluster')
    cluster_details = None
    cluster_choice = prompt_user_friendly_choice_list(
        "Which kubernetes cluster do you want to target?", cluster_choice_list)
    if cluster_choice == len(cluster_choice_list) - 1:
        cluster_name = prompt_not_empty('Please enter name of the cluster to be created: ')
        resource_group = get_resource_group()
        # check if cluster already exists
        for aks_cluster in aks_list:
            if cluster_name.lower() == aks_cluster['name'].lower() and aks_cluster['resourceGroup']:
                logger.warning('AKS cluster with the same name already exists. Using the existing cluster.')
                cluster_details = aks_cluster
        if not cluster_details:
            cluster_details = create_aks_cluster(cluster_name, resource_group)
    else:
        cluster_details = aks_list[cluster_choice]
    return cluster_details


def get_acr_details(name=None):
    _subscription_id, subscription_name, _tenant_id, _environment_name = get_default_subscription_info()
    logger.warning("Using your default Azure subscription %s for fetching Azure Container Registries.",
                   subscription_name)
    acr_list = subprocess.check_output('az acr list -o json', shell=True)
    acr_list = json.loads(acr_list)
    if not acr_list:
        return None

    registry_choice = 0
    registry_choice_list = []
    for acr_clusters in acr_list:
        if not name:
            registry_choice_list.append(acr_clusters['name'])
        elif name.lower() == acr_clusters['name'].lower():
            return acr_clusters
    if name is not None:
        raise CLIError('Container Registry with name {} could not be found. '
                       'Please check using command az acr list.'.format(name))
    registry_choice_list.append('Create a new Azure Container Registry')
    registry_choice = prompt_user_friendly_choice_list(
        "Which Azure Container Registry do you want to use?", registry_choice_list)
    acr_details = None
    if registry_choice == len(registry_choice_list) - 1:
        registry_name = prompt_not_empty('Please enter name of the Azure Container Registry to be created: ')
        for registry in acr_list:
            if registry_name.lower() == registry['name'].lower():
                logger.warning('Azure Container Registry with the same name already exists. '
                               'Using the existing registry.')
                acr_details = registry
        if not acr_details:
            sku = get_sku()
            resource_group = get_resource_group()
            acr_details = create_acr(registry_name, resource_group, sku)
    else:
        acr_details = acr_list[registry_choice]
    return acr_details


def get_functionapp_details(name=None):
    _subscription_id, subscription_name, _tenant_id, _environment_name = get_default_subscription_info()
    logger.warning("Using your default Azure subscription %s for fetching Functionapps.", subscription_name)
    functionapp_list = subprocess.check_output('az functionapp list -o json', shell=True)
    functionapp_list = json.loads(functionapp_list)
    if not functionapp_list:
        logger.debug("No Functionapp deployments found in your Azure subscription.")
    functionapp_choice = 0
    app_choice_list = []
    for app in functionapp_list:
        if not name:
            app_choice_list.append(app['name'])
        elif name.lower() == app['name'].lower():
            return app
    if name is not None:
        raise CLIError('Functionapp with name {} could not be found. Please check using command az functionapp list.'
                       .format(name))

    functionapp_choice = prompt_user_friendly_choice_list(
        "Which Functionapp do you want to target?", app_choice_list)
    return functionapp_list[functionapp_choice]


def get_sku():
    sku_list = ['Basic', 'Classic', 'Premium', 'Standard']
    sku_choice = prompt_user_friendly_choice_list(
        "Select the SKU of the container registry?", sku_list)
    return sku_list[sku_choice]


def configure_aks_credentials(cluster_name, resource_group):
    try:
        subscription_id, subscription_name, tenant_id, environment_name = get_default_subscription_info()
        logger.warning("Using your default Azure subscription %s for getting AKS cluster credentials.",
                       subscription_name)
        _aks_creds = subprocess.check_output(
            'az aks get-credentials -n {cluster_name} -g {group_name} -o json'.format(
                cluster_name=cluster_name, group_name=resource_group), shell=True)
    except Exception as ex:
        raise CLIError(ex)
