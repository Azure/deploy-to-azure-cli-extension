from knack.log import get_logger
from knack.util import CLIError
from azext_aks_deploy.dev.common.prompting import prompt_user_friendly_choice_list

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


def get_aks_details(name=None):
    import subprocess
    import json
    subscription_id, subscription_name, tenant_id, environment_name = get_default_subscription_info()
    logger.warning("Using your default Azure subscription %s for fetching AKS clusters.", subscription_name)
    aks_list = subprocess.check_output('az aks list -o json', shell=True)
    aks_list = json.loads(aks_list)
    if aks_list:
        cluster_choice = 0
        cluster_choice_list = []
        for aks_clusters in aks_list:
            if not name:
                cluster_choice_list.append(aks_clusters['name'])
            elif name.lower() == aks_clusters['name'].lower():
                return aks_clusters
        if name is not None:
            raise CLIError('Cluster with name {} could not be found. Please check using command az aks list.'.format(name))
        cluster_choice = prompt_user_friendly_choice_list(
            "Which kubernetes cluster do you want to target for this pipeline?", cluster_choice_list)
        return aks_list[cluster_choice]


def get_acr_details(name=None):
    import subprocess
    import json
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
        registry_choice = prompt_user_friendly_choice_list(
            "Which Azure Container Registry do you want to use for this pipeline?", registry_choice_list)
        return acr_list[registry_choice]

def configure_aks_credentials(cluster_name,resource_group):
    try:
        import subprocess
        import json
        subscription_id, subscription_name, tenant_id, environment_name = get_default_subscription_info()
        logger.warning("Using your default Azure subscription %s for getting AKS cluster credentials.", subscription_name)
        aks_creds = subprocess.check_output('az aks get-credentials -n {} -g {} -o json'.format(cluster_name,resource_group), shell=True)
    except Exception as ex:
        raise CLIError(ex)    