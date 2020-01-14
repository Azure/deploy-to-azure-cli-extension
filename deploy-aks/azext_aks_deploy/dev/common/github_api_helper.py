# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import requests
import time
from knack.log import get_logger
from knack.util import CLIError
from azext_aks_deploy.dev.common.prompting import prompt_not_empty
from azext_aks_deploy.dev.common.git import resolve_git_ref_heads, get_branch_name_from_ref

logger = get_logger(__name__)

_HTTP_NOT_FOUND_STATUS = 404
_HTTP_SUCCESS_STATUS = 200
_HTTP_CREATED_STATUS = 201


class Files:  # pylint: disable=too-few-public-methods
    def __init__(self, path, content):
        self.path = path
        self.content = content


def get_github_pat_token(token_prefix,display_warning=False):
    from azext_aks_deploy.dev.common.github_credential_manager import GithubCredentialManager
    github_manager = GithubCredentialManager()
    return github_manager.get_token(token_prefix=token_prefix,display_warning=display_warning)


def get_github_repos_api_url(repo_id):
    return 'https://api.github.com/repos/' + repo_id


def push_files_github(files, repo_name, branch, commit_to_branch, message="Setting up K8s deployment workflow",branch_name=None):
    if commit_to_branch:
        return commit_files_to_github_branch(files, repo_name, branch, message)
    # Pull request flow
    # Create Branch
    branch_name = create_github_branch(repo=repo_name, source=branch, new_branch=branch_name)
    # Commit files to branch
    commit_files_to_github_branch(files, repo_name, branch_name, message)
    # Create PR from new branch
    pr = create_pr_github(branch, branch_name, repo_name, message)
    print('Created a Pull Request - {url}'.format(url=pr['url']))


def create_pr_github(branch, new_branch, repo_name, message):
    """
    API Documentation - https://developer.github.com/v3/pulls/#create-a-pull-request
    """
    token = get_github_pat_token(repo_name)
    create_pr_url = 'https://api.github.com/repos/{repo_id}/pulls'.format(repo_id=repo_name)
    create_pr_request_body = {
        "title": message,
        "head": new_branch,
        "base": branch
    }
    create_response = requests.post(url=create_pr_url, auth=('', token),
                                    json=create_pr_request_body, headers=get_application_json_header())
    if not create_response.status_code == _HTTP_CREATED_STATUS:
        raise CLIError('Pull request creation failed. Error: ({err})'.format(err=create_response.reason))
    import json
    return json.loads(create_response.text)


def create_github_branch(repo, source, new_branch=None):
    """
    API Documentation - https://developer.github.com/v3/git/refs/#create-a-reference
    """
    token = get_github_pat_token(repo)
    # Validate new branch name is valid
    branch_is_valid = False
    if new_branch:
        ref, is_folder = get_github_branch(repo, new_branch)
        if not ref and not is_folder:
            branch_is_valid = True
        else:
            logger.warning('Not a valid branch name.')
    while not branch_is_valid:
        new_branch = prompt_not_empty(msg='Enter new branch name to create: ')
        ref, is_folder = get_github_branch(repo, new_branch)
        if not ref and not is_folder:
            branch_is_valid = True
        else:
            logger.warning('Not a valid branch name.')
    # Get source branch ref
    ref_item, is_folder = get_github_branch(repo, source)
    if not ref_item or is_folder:
        raise CLIError('Branch ({branch}) does not exist.'.format(branch=source))
    source_ref = ref_item['object']['sha']
    create_github_ref_url = 'https://api.github.com/repos/{repo_id}/git/refs'.format(repo_id=repo)
    create_github_ref_request_body = {
        "ref": resolve_git_ref_heads(new_branch),
        "sha": source_ref
    }
    create_response = requests.post(url=create_github_ref_url, auth=('', token),
                                    json=create_github_ref_request_body, headers=get_application_json_header())
    if not create_response.status_code == _HTTP_CREATED_STATUS:
        raise CLIError('Branch creation failed. Error: ({err})'.format(err=create_response.reason))
    return get_branch_name_from_ref(new_branch)


def get_github_branch(repo, branch):
    """
    API Documentation - https://developer.github.com/v3/repos/branches/#get-branch
    Returns branch, is_folder
    branch : None if the branch with this name does not exist else branch ref
    is_folder : True or False
    """
    token = get_github_pat_token(repo)
    head_ref_name = resolve_git_ref_heads(branch).lower()
    get_branch_url = 'https://api.github.com/repos/{repo_id}/git/{refs_heads_branch}'.format(
        repo_id=repo, refs_heads_branch=head_ref_name)
    get_response = requests.get(get_branch_url, auth=('', token))
    if get_response.status_code == _HTTP_NOT_FOUND_STATUS:
        return None, False
    if get_response.status_code == _HTTP_SUCCESS_STATUS:
        import json
        refs = json.loads(get_response.text)
        if isinstance(refs, list):
            if refs[0]['ref'].startswith(head_ref_name + '/'):
                logger.debug('Branch name is a folder hence invalid branch name.')
                return None, True
            # Parse and find correct branch
            for ref in refs:
                if ref['ref'] == head_ref_name:
                    return ref, False
            return None, False
        if refs['ref'] == head_ref_name:
            return refs, False
    raise CLIError('Cannot get branch ({branch})'.format(branch=branch))


def get_default_branch(repo):
    """
    API Documentation - https://developer.github.com/v3/repos/#get
    Returns default branch name
    """
    token = get_github_pat_token(repo)
    try:
        get_branch_url = 'https://api.github.com/repos/{repo}'.format(repo=repo)
        get_response = requests.get(get_branch_url, auth=('', token))
        repo_details = get_response.json()
        return repo_details['default_branch']
    except Exception as ex:
        CLIError(ex)    

def commit_files_to_github_branch(files, repo_name, branch, message):
    if files:
        for file in files:
            commit_sha = commit_file_to_github_branch(file.path, file.content, repo_name, branch, message)
        # returning last commit sha
        return commit_sha
    else:
        raise CLIError("No files to checkin.")


def get_application_json_header():
    return {'Content-Type': 'application/json' + '; charset=utf-8',
            'Accept': 'application/json'}


def get_application_json_header_for_preview():
    return {'Accept': 'application/vnd.github.antiope-preview+json'}


def commit_file_to_github_branch(path_to_commit, content, repo_name, branch, message):
    """
    API Documentation - https://developer.github.com/v3/repos/contents/#create-a-file
    """
    import base64
    headers = get_application_json_header()
    url_for_github_file_api = 'https://api.github.com/repos/{repo_name}/contents/{path_to_commit}'.format(
        repo_name=repo_name, path_to_commit=path_to_commit)
    if path_to_commit and content:
        path_to_commit = path_to_commit.strip('.')
        path_to_commit = path_to_commit.strip('/')
        encoded_content = base64.b64encode(content.encode('utf-8')).decode("utf-8")
        request_body = {
            "message": message,
            "branch": branch,
            "content": encoded_content
        }
        token = get_github_pat_token(repo_name)
        logger.warning('Checking in file %s in the Github repository %s', path_to_commit, repo_name)
        response = requests.put(url_for_github_file_api, auth=('', token),
                                json=request_body, headers=headers)
        logger.debug(response.text)
        if not response.status_code == _HTTP_CREATED_STATUS:
            raise CLIError('GitHub file checkin failed for file ({file}). Status Code ({code}).'.format(
                file=path_to_commit, code=response.status_code))
        else:
            commit_obj = response.json()['commit']
            commit_sha = commit_obj['sha']
            return commit_sha
    else:
        raise CLIError('GitHub file checkin failed. File path or content is empty.')


def get_languages_for_repo(repo_name):
    """
    API Documentation - https://developer.github.com/v3/repos/#list-languages
    """
    token = get_github_pat_token(repo_name)
    get_languagues_url = 'https://api.github.com/repos/{repo_id}/languages'.format(repo_id=repo_name)
    get_response = requests.get(url=get_languagues_url, auth=('', token))
    if not get_response.status_code == _HTTP_SUCCESS_STATUS:
        raise CLIError('Get Languages failed. Error: ({err})'.format(err=get_response.reason))
    import json
    return json.loads(get_response.text)

def get_check_runs_for_commit(repo_name,commmit_sha):
    """
    API Documentation - https://developer.github.com/v3/checks/runs/#list-check-runs-for-a-specific-ref
    """
    token = get_github_pat_token(repo_name)
    headers = get_application_json_header_for_preview()
    time.sleep(1)
    get_check_runs_url = 'https://api.github.com/repos/{repo_id}/commits/{ref}/check-runs'.format(repo_id=repo_name,ref=commmit_sha)
    get_response = requests.get(url=get_check_runs_url, auth=('', token), headers=headers)
    if not get_response.status_code == _HTTP_SUCCESS_STATUS:
        raise CLIError('Get Check Runs failed. Error: ({err})'.format(err=get_response.reason))
    import json
    return json.loads(get_response.text)


def get_work_flow_check_runID(repo_name,commmit_sha):
    check_run_found= False
    count = 0
    while(not check_run_found or count>3):
        check_runs_list_response = get_check_runs_for_commit(repo_name,commmit_sha)
        if check_runs_list_response and check_runs_list_response['total_count'] > 0:
            # fetch the Github actions check run and its check run ID
            check_runs_list = check_runs_list_response['check_runs']
            for check_run in check_runs_list:
                if check_run['app']['slug'] == 'github-actions':
                    check_run_id = check_run['id']
                    check_run_found = True
                    return check_run_id
        time.sleep(5)
        count = count+1
    raise CLIError("Couldn't find Github Actions check run. Please check 'Actions' tab in your Github repo.")
    

def get_check_run_status_and_conclusion(repo_name, check_run_id):
    """
    API Documentation - https://developer.github.com/v3/checks/runs/#get-a-single-check-run
    """
    token = get_github_pat_token(repo_name)
    headers = get_application_json_header_for_preview()
    get_check_run_url = 'https://api.github.com/repos/{repo_id}/check-runs/{checkID}'.format(repo_id=repo_name,checkID=check_run_id)
    get_response = requests.get(url=get_check_run_url, auth=('', token), headers=headers)
    if not get_response.status_code == _HTTP_SUCCESS_STATUS:
        raise CLIError('Get Check Run failed. Error: ({err})'.format(err=get_response.reason))
    import json
    return json.loads(get_response.text)['status'], json.loads(get_response.text)['conclusion']
    