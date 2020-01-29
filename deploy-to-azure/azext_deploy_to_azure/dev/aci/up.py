# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError
from knack.log import get_logger
from knack.prompting import prompt

from azext_deploy_to_azure.dev.common.git import resolve_repository
from azext_deploy_to_azure.dev.common.github_api_helper import (Files, get_work_flow_check_runID,
                                                                push_files_to_repository,
                                                                get_languages_for_repo,
                                                                get_github_pat_token,
                                                                get_default_branch,
                                                                check_file_exists)
from azext_deploy_to_azure.dev.common.github_workflow_helper import poll_workflow_status, get_new_workflow_yaml_name
from azext_deploy_to_azure.dev.common.github_azure_secrets import get_azure_credentials
from azext_deploy_to_azure.dev.common.const import (CHECKIN_MESSAGE_ACI, APP_NAME_DEFAULT, APP_NAME_PLACEHOLDER,
                                                    ACR_PLACEHOLDER, RG_PLACEHOLDER, PORT_NUMBER_DEFAULT,
                                                    PORT_NUMBER_PLACEHOLDER)
from azext_deploy_to_azure.dev.aks.docker_helm_template import get_docker_templates

logger = get_logger(__name__)
aci_token_prefix = "AciUpCLIExt_"


# pylint: disable=too-many-statements
def aci_up(acr=None, repository=None, port=None, branch_name=None,
           skip_secrets_generation=False, do_not_wait=False):
    """Build and Deploy to Azure Container Instances using GitHub Actions
    :param acr: Name of the Azure Container Registry to be used for pushing the image
    :type acr: string
    :param repository: GitHub Repository URL e.g. https://github.com/contoso/webapp.
    :type repository: string
    :param port: Port on which your application runs. Default is 8080
    :type port: str
    :param branch_name: New Branch Name to be created to check in files and raise a PR
    :type branch_name: str
    :param skip_secrets_generation: Skip Generation of Azure Credentials
    :type skip_secrets_generation: bool
    :param do_not_wait: Do not wait for Workflow Completion
    :type do_not_wait: bool
    """
    # TODO: Use the ACI Deploy Action when Published
    repo_name, repository = resolve_repository(repository)

    get_github_pat_token(token_prefix=aci_token_prefix + repo_name, display_warning=True)
    logger.warning("Setting up your workflow")
    languages = get_languages_for_repo(repo_name)
    if not languages:
        raise CLIError("Language detection failed for this repository")

    language = choose_supported_language(languages)
    if language:
        logger.warning('%s Repository Detected.', language)
    else:
        logger.debug('Languages detected: %s', languages)
        raise CLIError("The language in this repository are not yet supported from up command.")

    from azext_deploy_to_azure.dev.common.azure_cli_resources import get_acr_details
    acr_details = get_acr_details(acr)
    logger.debug(acr_details)
    print('')

    files = []
    if port is None:
        port = PORT_NUMBER_DEFAULT
    if 'Dockerfile' not in languages.keys():
        # check in Dockerfile and Dockerignore
        docker_files = get_docker_templates(language, port)
        if docker_files:
            files = files + docker_files
    else:
        logger.warning('Using the Dockerfile found in repository %s', repo_name)

    # create Azure Service Principal and display JSON on the screen for the user to configure it as GitHub Secrets
    if not skip_secrets_generation:
        get_azure_credentials()

    print('')
    workflow_files = get_yaml_template_for_repo(acr_details, repo_name, port)
    if workflow_files:
        files = files + workflow_files

    # File checkin
    for file_name in files:
        logger.debug("Checkin file path: %s", file_name.path)
        logger.debug("Checkin file content: %s", file_name.content)

    default_branch = get_default_branch(repo_name)
    workflow_commit_sha = push_files_to_repository(
        repo_name=repo_name, default_branch=default_branch, files=files,
        branch_name=branch_name, message=CHECKIN_MESSAGE_ACI
    )
    if workflow_commit_sha:
        print('Creating workflow...')
        check_run_id = get_work_flow_check_runID(repo_name, workflow_commit_sha)
        workflow_url = 'https://github.com/{repo_id}/runs/{checkID}'.format(repo_id=repo_name,
                                                                            checkID=check_run_id)
        print('GitHub Action Workflow has been created - {}'.format(workflow_url))

        if not do_not_wait:
            poll_workflow_status(repo_name, check_run_id)
            list_name = repo_name.split("/")
            app_name = list_name[1].lower()
            app_url = get_app_url(acr_details, app_name)
            app_url_with_port = app_url + ":" + port + "/"
            print('Your app is deployed at: ', app_url_with_port)


def choose_supported_language(languages):
    # check if one of top three languages are supported or not
    list_languages = list(languages.keys())
    first_language = list_languages[0]
    if first_language in ('JavaScript', 'Java', 'Python'):
        return first_language
    if len(list_languages) >= 1 and list_languages[1] in ('JavaScript', 'Java', 'Python'):
        return list_languages[1]
    if len(list_languages) >= 2 and list_languages[2] in ('JavaScript', 'Java', 'Python'):
        return list_languages[2]
    return None


def get_yaml_template_for_repo(acr_details, repo_name, port):
    files_to_return = []
    github_workflow_path = '.github/workflows/'
    yaml_file_name = 'main.yml'
    workflow_yaml = github_workflow_path + yaml_file_name
    list_name = repo_name.split("/")
    APP_NAME_DEFAULT = list_name[1].lower()
    if check_file_exists(repo_name, workflow_yaml):
        yaml_file_name = get_new_workflow_yaml_name()
        workflow_yaml = github_workflow_path + yaml_file_name
    from azext_deploy_to_azure.dev.resources.resourcefiles import DEPLOY_TO_ACI_TEMPLATE
    files_to_return.append(Files(path=workflow_yaml,
                                 content=DEPLOY_TO_ACI_TEMPLATE
                                 .replace(APP_NAME_PLACEHOLDER, APP_NAME_DEFAULT)
                                 .replace(ACR_PLACEHOLDER, acr_details['name'])
                                 .replace(RG_PLACEHOLDER, acr_details['resourceGroup'])
                                 .replace(PORT_NUMBER_PLACEHOLDER, port)))
    return files_to_return


def get_app_url(acr_details, app_name):
    import subprocess as sb
    resource_group = acr_details['resourceGroup']
    url_find_command = 'az container show \
        --name {app_name} --resource-group {resource_group_name} \
            --query ipAddress.fqdn'.format(app_name=app_name, resource_group_name=resource_group)
    url_result = sb.check_output(url_find_command, shell=True)
    url_result = url_result.decode().strip().lstrip('\"').rstrip('\"')
    app_url = "http://" + url_result
    return app_url
