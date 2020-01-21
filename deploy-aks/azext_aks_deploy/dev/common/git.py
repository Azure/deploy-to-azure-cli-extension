# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

from knack.log import get_logger
from knack.util import CLIError
from knack.prompting import prompt


logger = get_logger(__name__)


def resolve_repository(repository_url, detect=True):
    """
    Resolve repo url from-
    1. Input parameter
    2. Local repo context, if detect is true
    3. User input
    """
    if not repository_url and detect:
        repository_url = get_repository_url_from_local_repo()
        logger.debug('Github Remote url detected local repo is %s', repository_url)
    if not repository_url:
        repository_url = prompt('GitHub Repository url (e.g. https://github.com/azure/azure-cli):')
    if not repository_url:
        raise CLIError('The following arguments are required: --repository.')
    repository_name = get_repo_name_from_repo_url(repository_url)
    return repository_name, repository_url


def get_repo_name_from_repo_url(repository_url):
    """
    Should be called with a valid github url
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


def get_repository_url_from_local_repo():
    return get_remote_url(is_github_url_candidate)


def uri_parse(url):
    return urlparse(url)


def is_github_url_candidate(url):
    if url is None:
        return False
    components = uri_parse(url.lower())
    if components.netloc == 'github.com':
        return True
    return False


def get_remote_url(validation_function=None):
    remotes = get_git_remotes()
    if remotes is not None:
        if _ORIGIN_PUSH_KEY in remotes and (validation_function is None or
                                            validation_function(remotes[_ORIGIN_PUSH_KEY])):
            return remotes[_ORIGIN_PUSH_KEY]
        for k, value in remotes.items():
            if k != _ORIGIN_PUSH_KEY and k.endswith('(push)') and (validation_function is None or
                                                                   validation_function(value)):
                return value
    return None


def get_git_remotes():
    import subprocess
    import sys
    if _git_remotes:
        return _git_remotes
    try:
        # Example output:
        # git remote - v
        # full  https://mseng.visualstudio.com/DefaultCollection/VSOnline/_git/_full/VSO (fetch)
        # full  https://mseng.visualstudio.com/DefaultCollection/VSOnline/_git/_full/VSO (push)
        # origin  https://mseng.visualstudio.com/defaultcollection/VSOnline/_git/VSO (fetch)
        # origin  https://mseng.visualstudio.com/defaultcollection/VSOnline/_git/VSO (push)
        output = subprocess.check_output([_GIT_EXE, 'remote', '-v'], stderr=subprocess.STDOUT)
    except BaseException as ex:  # pylint: disable=broad-except
        logger.info('GitDetect: Could not detect current remotes based on current working directory.')
        logger.debug(ex, exc_info=True)
        return None
    if sys.stdout.encoding is not None:
        lines = output.decode(sys.stdout.encoding).split('\n')
    else:
        lines = output.decode().split('\n')
    for line in lines:
        components = line.strip().split()
        if len(components) == 3:
            _git_remotes[components[0] + components[2]] = components[1]
    return _git_remotes


def resolve_git_ref_heads(ref):
    """Prepends 'refs/heads/' prefix to ref str if not already there.
    :param ref: The text to validate.
    :type ref: str
    :rtype: str
    """
    if ref is not None and not ref.startswith(REF_HEADS_PREFIX) and not ref.startswith(REF_PULL_PREFIX):
        ref = REF_HEADS_PREFIX + ref
    return ref


def get_branch_name_from_ref(ref):
    """Removes 'refs/heads/' prefix from ref str if there.
    :param ref: The text to validate.
    :type ref: str
    :rtype: str
    """
    if ref is not None and ref.startswith(REF_HEADS_PREFIX):
        ref = ref[len(REF_HEADS_PREFIX):]
    return ref


_git_remotes = {}
_GIT_EXE = 'git'
_ORIGIN_PUSH_KEY = 'origin(push)'
REF_HEADS_PREFIX = 'refs/heads/'
REF_PULL_PREFIX = 'refs/pull/'
