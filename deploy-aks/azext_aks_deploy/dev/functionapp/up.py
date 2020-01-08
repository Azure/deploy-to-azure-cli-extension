# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.prompting import prompt
from knack.log import get_logger
from knack.util import CLIError

from azext_aks_deploy.dev.common.git import get_repository_url_from_local_repo, uri_parse
from azext_aks_deploy.dev.common.github_api_helper import (Files, get_work_flow_check_runID, get_languages_for_repo,
                                                           push_files_github, get_check_run_status_and_conclusion,
                                                           get_github_pat_token)
from azext_aks_deploy.dev.common.github_workflow_helper import poll_workflow_status
from azext_aks_deploy.dev.common.github_azure_secrets import get_azure_credentials
from azext_aks_deploy.dev.common.utils import get_repo_name_from_repo_url
from azext_aks_deploy.dev.common.const import ( APP_NAME_DEFAULT, APP_NAME_PLACEHOLDER)

logger = get_logger(__name__)

def functionapp_deploy(repository=None, skip_secrets_generation=False, no_wait=False):
    """Build and Deploy to Azure FunctionApp via GitHub actions
    :param repository: GitHub repository URL e.g. https://github.com/azure/azure-cli.
    :type repository: str
    :param skip_secrets_generation : Flag to skip generating Azure credentials.
    :type skip_secrets_generation: bool
    :param no_wait : Do not wait for workflow completion.
    :type no_wait bool
    """
    if repository is None:
        repository = get_repository_url_from_local_repo()
        logger.debug('Github Remote url detected local repo is {}'.format(repository))
    if not repository:
        repository = prompt('GitHub Repository url (e.g. https://github.com/atbagga/aks-deploy):')
    if not repository:
        raise CLIError('The following arguments are required: --repository.')
    repo_name = get_repo_name_from_repo_url(repository)

    get_github_pat_token(repo_name,display_warning=True)
    logger.warning('Setting up your workflow.')                                                           

    from azext_aks_deploy.dev.common.azure_cli_resources import (get_default_subscription_info,
                                                                 get_functionapp_details,
                                                                 configure_aks_credentials)

    # create azure service principal and display json on the screen for user to configure it as Github secrets
    if not skip_secrets_generation:
        get_azure_credentials()
        
    print('')
    files = get_yaml_template_for_repo()
    
    # File checkin
    for file_name in files:
        logger.debug("Checkin file path: {}".format(file_name.path))
        logger.debug("Checkin file content: {}".format(file_name.content))

    workflow_commit_sha = push_files_github(files, repo_name, 'master', True, message="Setting up K8s deployment workflow.")
    print('Creating workflow...')
    check_run_id = get_work_flow_check_runID(repo_name, workflow_commit_sha)
    workflow_url = 'https://github.com/{repo_id}/runs/{checkID}'.format(repo_id=repo_name, checkID=check_run_id)
    print('GitHub Action workflow has been created - {}'.format(workflow_url))

    if not do_not_wait:
        poll_workflow_status(repo_name, check_run_id)
    return


def get_yaml_template_for_repo(language, functionapp_name, repo_name):
    files_to_return = []
    # Read template file
    return None
       

def choose_supported_language(languages):
    # check if top three languages are supported or not
    list_languages = list(languages.keys())
    first_language = list_languages[0]
    if 'JavaScript' == first_language or 'Java' == first_language or 'Python' == first_language:
        return first_language
    elif len(list_languages) >= 1 and ( 'JavaScript' == list_languages[1] or 'Java' == list_languages[1] or 'Python' == list_languages[1]):
        return list_languages[1]
    elif len(list_languages) >= 2 and ( 'JavaScript' == list_languages[2] or 'Java' == list_languages[2] or 'Python' == list_languages[2]):
        return list_languages[2]
    return None
    
