# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from knack.log import get_logger
from knack.util import CLIError

from azext_deploy_to_azure.dev.common.git import resolve_repository
from azext_deploy_to_azure.dev.common.github_api_helper import (Files, get_work_flow_check_runID,
                                                                push_files_to_repository,
                                                                get_languages_for_repo,
                                                                get_github_pat_token,
                                                                get_default_branch,
                                                                check_file_exists)
from azext_deploy_to_azure.dev.common.github_workflow_helper import poll_workflow_status
from azext_deploy_to_azure.dev.common.github_azure_secrets import get_azure_credentials_functionapp
from azext_deploy_to_azure.dev.common.const import CHECKIN_MESSAGE_FUNCTIONAPP

logger = get_logger(__name__)
functionapp_token_prefix = "FunctionAppUpCLIExt_"


def functionapp_deploy(app_name=None, repository=None, skip_secrets_generation=False,
                       branch_name=None, do_not_wait=False):
    """Setup GitHub Action to build and deploy to Azure FunctionApp
    :param repository: GitHub repository URL e.g. https://github.com/azure/azure-cli.
    :type repository: str
    :param app_name: FunctionApp name in the subscription.
    :type app_name: str

    :param branch_name: New branch name to be created to check in files and raise a PR
    :type branch_name:str
    :param skip_secrets_generation : Flag to skip generating Azure credentials.
    :type skip_secrets_generation: bool
    :param do_not_wait : Do not wait for workflow completion.
    :type do_not_wait bool
    """
    repo_name, repository = resolve_repository(repository)

    get_github_pat_token(token_prefix=functionapp_token_prefix + repo_name, display_warning=True)
    logger.warning('Setting up your workflow.')

    languages = get_languages_for_repo(repo_name)
    if not languages:
        raise CLIError('Language detection failed for this repository.')
    language = choose_supported_language(languages)
    if language:
        logger.warning('%s repository detected.', language)
    else:
        logger.debug('Languages detected : %s', languages)
        raise CLIError('The languages in this repository are not yet supported from up command.')

    # assuming the host.json is in the root directory for now
    ensure_function_app(repo_name=repo_name)

    from azext_deploy_to_azure.dev.common.azure_cli_resources import get_functionapp_details
    app_details = get_functionapp_details(app_name)
    logger.debug(app_details)
    app_name = app_details['name']
    platform = "linux" if "linux" in app_details['kind'] else "windows"

    # create azure service principal and display json on the screen for user to configure it as Github secrets
    if not skip_secrets_generation:
        get_azure_credentials_functionapp(app_name)

    print('')
    files = get_functionapp_yaml_template_for_repo(app_name, repo_name, language, platform)

    # File checkin
    for file_name in files:
        logger.debug("Checkin file path: %s", file_name.path)
        logger.debug("Checkin file content: %s", file_name.content)

    default_branch = get_default_branch(repo_name)
    workflow_commit_sha = push_files_to_repository(
        files=files, default_branch=default_branch, repo_name=repo_name, branch_name=branch_name,
        message=CHECKIN_MESSAGE_FUNCTIONAPP)
    print('Creating workflow...')
    check_run_id = get_work_flow_check_runID(repo_name, workflow_commit_sha)
    workflow_url = 'https://github.com/{repo_id}/runs/{checkID}'.format(repo_id=repo_name, checkID=check_run_id)
    print('GitHub Action workflow has been created - {}'.format(workflow_url))

    if not do_not_wait:
        poll_workflow_status(repo_name, check_run_id)


def ensure_function_app(repo_name, path=None):
    if path:
        path_to_host = path
    else:
        path_to_host = 'host.json'
    if check_file_exists(repo_name, path_to_host):
        logger.debug("Host.json was found at %s", path_to_host)
    else:
        raise CLIError('host.json could not be located at {}.'.format(path_to_host))


def get_functionapp_yaml_template_for_repo(app_name, repo_name, language, platform):
    files_to_return = []
    github_workflow_path = '.github/workflows/'
    # Read template file
    yaml_file_name = 'main.yml'
    workflow_yaml = github_workflow_path + yaml_file_name
    if check_file_exists(repo_name, workflow_yaml):
        from azext_deploy_to_azure.dev.common.github_workflow_helper import get_new_workflow_yaml_name
        yaml_file_name = get_new_workflow_yaml_name()
        workflow_yaml = github_workflow_path + yaml_file_name
    from azext_deploy_to_azure.dev.common.const import APP_NAME_PLACEHOLDER
    files_to_return.append(Files(path=workflow_yaml,
                                 content=get_language_to_workflow_mapping(language, platform)
                                 .replace(APP_NAME_PLACEHOLDER, app_name)))
    return files_to_return


def choose_supported_language(languages):
    # check if one of top three languages are supported or not
    list_languages = list(languages.keys())
    if list_languages and list_languages[0] in ('JavaScript', 'Java', 'Python', 'PowerShell', "C#"):
        return list_languages[0]
    if len(list_languages) >= 1 and list_languages[1] in ('JavaScript', 'Java', 'Python', 'PowerShell', "C#"):
        return list_languages[1]
    if len(list_languages) >= 2 and list_languages[2] in ('JavaScript', 'Java', 'Python', 'PowerShell', "C#"):
        return list_languages[2]
    return None


def get_language_to_workflow_mapping(language, platform):
    from azext_deploy_to_azure.dev.resources.resourcefiles import (
        DEPLOY_TO_FUNCTIONAPP_PYTHON_LINUX_TEMPLATE,
        DEPLOY_TO_FUNCTIONAPP_NODE_WINDOWS_TEMPLATE,
        DEPLOY_TO_FUNCTIONAPP_NODE_LINUX_TEMPLATE,
        DEPLOY_TO_FUNCTIONAPP_POWERSHELL_WINDOWS_TEMPLATE,
        DEPLOY_TO_FUNCTIONAPP_JAVA_WINDOWS_TEMPLATE,
        DEPLOY_TO_FUNCTIONAPP_DOTNET_WINDOWS_TEMPLATE,
        DEPLOY_TO_FUNCTIONAPP_DOTNET_LINUX_TEMPLATE)

    workflow_map = {
        "linux": {
            "JavaScript": DEPLOY_TO_FUNCTIONAPP_NODE_LINUX_TEMPLATE,
            "Python": DEPLOY_TO_FUNCTIONAPP_PYTHON_LINUX_TEMPLATE,
            "PowerShell": "",
            "Java": "",
            "C#": DEPLOY_TO_FUNCTIONAPP_DOTNET_LINUX_TEMPLATE},
        "windows": {
            "JavaScript": DEPLOY_TO_FUNCTIONAPP_NODE_WINDOWS_TEMPLATE,
            "Python": "",
            "PowerShell": DEPLOY_TO_FUNCTIONAPP_POWERSHELL_WINDOWS_TEMPLATE,
            "Java": DEPLOY_TO_FUNCTIONAPP_JAVA_WINDOWS_TEMPLATE,
            "C#": DEPLOY_TO_FUNCTIONAPP_DOTNET_WINDOWS_TEMPLATE}}
    if workflow_map[platform][language]:
        return workflow_map[platform][language]
    logger.debug("Language: %s, Platform: %s", language, platform)
    raise CLIError("The selected repository language and Azure Functions platform are not supported.")
