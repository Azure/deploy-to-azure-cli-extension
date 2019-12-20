# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.prompting import prompt
from knack.log import get_logger
from knack.util import CLIError

from azext_aks_deploy.dev.common.git import get_repository_url_from_local_repo, uri_parse
from azext_aks_deploy.dev.common.github_api_helper import (Files, get_work_flow_check_runID ,
                                                     get_check_run_status_and_conclusion ,get_github_pat_token)
from azext_aks_deploy.dev.common.github_azure_secrets import get_azure_credentials
from azext_aks_deploy.dev.common.kubectl import get_deployment_IP_port
from azext_aks_deploy.dev.resources.docker_helm_template import get_docker_and_helm_charts,choose_supported_language

logger = get_logger(__name__)

def aks_deploy(aks_cluster=None, acr=None, repository=None, skip_secrets_generation=False, do_not_wait=False):
    """Build and Deploy to AKS via GitHub actions
    :param aks_cluster: Name of the cluster to select for deployment.
    :type aks_cluster: str
    :param acr: Name of the Azure Container Registry to be used for pushing the image.
    :type acr: str
    :param repository: GitHub repository URL e.g. https://github.com/azure/azure-cli.
    :type repository: str
    :param skip_secrets_generation : Flag to skip generating Azure credentials.
    :type skip_secrets_generation: bool
    :param do_not_wait : Do not wait for workflow completion.
    :type do_not_wait bool
    """
    if repository is None:
        repository = get_repository_url_from_local_repo()
        logger.debug('Github Remote url detected local repo is {}'.format(repository))
    if not repository:
        repository = prompt('GitHub Repository url (e.g. https://github.com/atbagga/aks-deploy):')
    if not repository:
        raise CLIError('The following arguments are required: --repository.')
    repo_name = _get_repo_name_from_repo_url(repository)

    from azext_aks_deploy.dev.common.github_api_helper import get_languages_for_repo, push_files_github
    get_github_pat_token(display_warning=True)                                                              
    languages = get_languages_for_repo(repo_name)
    if not languages:
        raise CLIError('Language detection has failed on this repository.')
    elif 'Dockerfile' not in languages.keys():
        docker_and_helm_charts = get_docker_and_helm_charts(languages)
        if docker_and_helm_charts:
            push_files_github(docker_and_helm_charts, repo_name, 'master', True, 
                              message="Checking in dockerfile for K8s deployment workflow.")
    from azext_aks_deploy.dev.common.azure_cli_resources import (get_default_subscription_info,
                                                                 get_aks_details,
                                                                 get_acr_details)
    
    cluster_details = get_aks_details(aks_cluster)
    logger.debug(cluster_details)
    acr_details = get_acr_details(acr)
    logger.debug(acr_details)
    # create azure service principal and display json on the screen for user to configure it as Github secrets
    if not skip_secrets_generation:
        get_azure_credentials()

    files = get_yaml_template_for_repo(languages, cluster_details, acr_details, repo_name)
    # File checkin
    logger.warning('Setting up your workflow. This will require 1 or more files to be checkedin to the repository.')
    for file_name in files:
        logger.debug("Checkin file path: {}".format(file_name.path))
        logger.debug("Checkin file content: {}".format(file_name.content))

    workflow_commit_sha = push_files_github(files, repo_name, 'master', True, message="Setting up K8s deployment workflow.")
    print('')
    print('GitHub workflow is setup for continuous deployment.')
    check_run_id = get_work_flow_check_runID(repo_name,workflow_commit_sha)
    workflow_url = 'https://github.com/{repo_id}/runs/{checkID}'.format(repo_id=repo_name,checkID=check_run_id)
    print('For more details, check {}'.format(workflow_url))
    print('')
    if not do_not_wait:
        poll_workflow_status(repo_name,check_run_id)
        deployment_ip, port = get_deployment_IP_port(APP_NAME_DEFAULT)
        print('Your app is deployed at :http://{ip}:{port}'.format(ip=deployment_ip,port=port))
    return


def poll_workflow_status(repo_name,check_run_id):
    import colorama
    import humanfriendly
    import time
    check_run_status = None
    check_run_status, check_run_conclusion= get_check_run_status_and_conclusion(repo_name, check_run_id)
    if check_run_status == 'queued':
        # When workflow status is Queued
        colorama.init()
        with humanfriendly.Spinner(label="Workflow is in queue") as spinner:
            while True:
                spinner.step()
                time.sleep(0.5)
                check_run_status, check_run_conclusion = get_check_run_status_and_conclusion(repo_name, check_run_id)
                if check_run_status == 'in_progress' or check_run_status == 'completed':
                    break
        colorama.deinit()
    if check_run_status == 'in_progress':
        # When workflow status is inprogress
        colorama.init()
        with humanfriendly.Spinner(label="Workflow is in progress") as spinner:
            while True:
                spinner.step()
                time.sleep(0.5)
                check_run_status, check_run_conclusion = get_check_run_status_and_conclusion(repo_name, check_run_id)
                if check_run_status == 'completed':
                    break
        colorama.deinit()
    print('GitHub workflow completed.')
    print('')
    if check_run_conclusion == 'success':
        print('Workflow succeeded')
    else:
        raise CLIError('Workflow failed!')


def get_yaml_template_for_repo(languages, cluster_details, acr_details, repo_name):
    language = choose_supported_language(languages)
    if language:
        logger.warning('%s repository detected.', language)
        files_to_return = []
        # Read template file
        from azext_aks_deploy.dev.resources.resourcefiles import DEPLOY_TO_AKS_TEMPLATE, DEPLOYMENT_MANIFEST, SERVICE_MANIFEST
        
        files_to_return.append(Files(path='manifests/service.yml',
            content=SERVICE_MANIFEST
                .replace(APP_NAME_PLACEHOLDER, APP_NAME_DEFAULT)
                .replace(PORT_NUMBER_PLACEHOLDER, PORT_NUMBER_DEFAULT)))
        files_to_return.append(Files(path='manifests/deployment.yml',
            content=DEPLOYMENT_MANIFEST
                .replace(APP_NAME_PLACEHOLDER, APP_NAME_DEFAULT)
                .replace(ACR_PLACEHOLDER, acr_details['name'])
                .replace(PORT_NUMBER_PLACEHOLDER, PORT_NUMBER_DEFAULT)))
        files_to_return.append(Files(path='.github/workflows/main.yml',
            content=DEPLOY_TO_AKS_TEMPLATE
                .replace(APP_NAME_PLACEHOLDER, APP_NAME_DEFAULT)
                .replace(ACR_PLACEHOLDER, acr_details['name'])
                .replace(CLUSTER_PLACEHOLDER, cluster_details['name'])
                .replace(RG_PLACEHOLDER, cluster_details['resourceGroup'])))
        return files_to_return
    else:
        logger.debug('Languages detected : {} '.format(languages))
        raise CLIError('The languages in this repository are not yet supported from up command.')

    
def _get_repo_name_from_repo_url(repository_url):
    """
    Should be called with a valid github or azure repo url
    returns owner/reponame for github repos, repo_name for azure repo type
    """
    parsed_url = uri_parse(repository_url)
    logger.debug('Parsing GitHub url: %s', parsed_url)
    if parsed_url.scheme == 'https' and parsed_url.netloc == 'github.com':
        logger.debug('Parsing path in the url to find repo id.')
        stripped_path = parsed_url.path.strip('/')
        if stripped_path.endswith('.git'):
            stripped_path = stripped_path[:-4]
        return stripped_path
    raise CLIError('Could not parse repository url.')


ACR_PLACEHOLDER = 'container_registry_name_place_holder'
APP_NAME_PLACEHOLDER = 'app_name_place_holder'
PORT_NUMBER_PLACEHOLDER = 'port_number_place_holder'
CLUSTER_PLACEHOLDER = 'cluster_name_place_holder'
RG_PLACEHOLDER = 'resource_name_place_holder'

PORT_NUMBER_DEFAULT = '8080'
APP_NAME_DEFAULT = 'k8sdemo'
