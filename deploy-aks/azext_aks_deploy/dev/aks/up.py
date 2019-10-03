# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.prompting import prompt
from knack.log import get_logger
from knack.util import CLIError

from azext_aks_deploy.dev.common.git import get_repository_url_from_local_repo, uri_parse
from azext_aks_deploy.dev.common.github_api_helper import Files

logger = get_logger(__name__)

def aks_deploy(aks_cluster=None, acr=None, repository=None):
    """Build and Deploy to AKS via GitHub actions
    """
    if repository is None:
        repository = get_repository_url_from_local_repo()
        logger.debug('Github Remote url detected local repo is {}'.format(repository))
    if not repository:
        raise CLIError('The following arguments are required: --repository.')
    repo_name = _get_repo_name_from_repo_url(repository)

    from azext_aks_deploy.dev.common.github_api_helper import get_languages_for_repo
    languages = get_languages_for_repo(repo_name)
    if not languages:
        raise CLIError('Language detection has failed on this repository.')
    from azext_aks_deploy.dev.common.azure_cli_resources import (get_default_subscription_info,
                                                                 get_aks_details,
                                                                 get_acr_details)
    if aks_cluster is None:
        cluster_details = get_aks_details(aks_cluster)
        logger.debug(cluster_details)
    if acr is None:
        acr_details = get_acr_details(acr)
        logger.debug(acr_details)
    files = get_yaml_template_for_repo(languages.keys())
    # File checkin
    logger.warning('Setting up your workflow.')
    for file_name in files:
        logger.warning("Checkin file path: {}".format(file_name.path))
        logger.debug("Checkin file content: {}".format(file_name.content))
    return {"Status": "Success"}


def get_yaml_template_for_repo(languages):
    if 'JavaScript' in languages and 'Dockerfile' in languages:
        logger.warning('Nodejs with dockerfile repository detected.')
        files_to_return = []
        # Read template file
        from azext_aks_deploy.dev.resources.resourcefiles import DEPLOY_TO_AKS_TEMPLATE, DEPLOYMENT_MANIFEST, SERVICE_MANIFEST
        files_to_return.append(Files(path='.github/workflows/main.yml', content=DEPLOY_TO_AKS_TEMPLATE))
        files_to_return.append(Files(path='manifests/service.yml', content=SERVICE_MANIFEST))
        files_to_return.append(Files(path='manifests/deployment.yml', content=DEPLOYMENT_MANIFEST))
        return files_to_return
    elif 'Java' in languages and 'Dockerfile' in languages:
        logger.warning('Java app with dockerfile repository detected.')
        return ['javafile1','javafile2', 'javafile3']
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

