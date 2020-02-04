# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.log import get_logger
from knack.prompting import prompt
from azext_deploy_to_azure.dev.common.prompting import prompt_user_friendly_choice_list
from azext_deploy_to_azure.dev.common.azure_cli_resources import get_default_subscription_info
from azext_deploy_to_azure.dev.common.github_api_helper import check_secret_exists, create_repo_secret

logger = get_logger(__name__)


def get_azure_credentials():
    import subprocess
    import json
    _subscription_id, _subscription_name, _tenant_id, _environment_name = get_default_subscription_info()
    azure_creds_user_choice = 1
    print('')
    print('You need to include the following key value pairs as part of your Secrets in the GitHub Repo Setting.')
    print('Please go to your GitHub Repo page -> Settings -> Secrets -> '
          'Add a new secret and include the following Name and value pairs.')
    while azure_creds_user_choice == 1:
        print('Creating AZURE_CREDENTIALS secret...')
        auth_details = subprocess.check_output('az ad sp create-for-rbac --sdk-auth -o json', shell=True)
        auth_details_json = json.loads(auth_details)
        print('')
        print('Name: AZURE_CREDENTIALS')
        print('Value:')
        print(json.dumps(auth_details_json, indent=2))
        print('')
        print('Creating REGISTRY_USERNAME and REGISTRY_PASSWORD...')
        sp_details = subprocess.check_output('az ad sp create-for-rbac -o json', shell=True)
        sp_details_json = json.loads(sp_details)
        print('')
        print('Name: REGISTRY_USERNAME')
        print('Value: ', sp_details_json['appId'])
        print('')
        print('Name: REGISTRY_PASSWORD')
        print('Value: ', sp_details_json['password'])
        print('')
        user_choice_list = []
        user_choice_list.append('Yes. Continue')
        user_choice_list.append('No. Re-generate the values for AZURE_CREDENTIALS, '
                                'REGISTRY_USERNAME and REGISTRY_PASSWORD')
        azure_creds_user_choice = prompt_user_friendly_choice_list(
            'Have you copied the name and value for AZURE_CREDENTIALS, REGISTRY_USERNAME and REGISTRY_PASSWORD:',
            user_choice_list)

def configure_azure_secrets(repo_name):
    if not check_secret_exists(repo_name,'AZURE_SECRET_NAME'):
        create_repo_secret(repo_name,'AZURE_SECRET_NAME','some new secret')
    

def get_azure_credentials_functionapp(app_name):
    import subprocess
    import json
    _subscription_id, _subscription_name, _tenant_id, _environment_name = get_default_subscription_info()
    print('')
    print('You need to include the following key value pairs as part of your Secrets in the GitHub Repo Setting.')
    print('Please go to your GitHub Repo page -> Settings -> Secrets -> '
          'Add a new secret and include the following Name and value pairs.')
    print('Creating AZURE_CREDENTIALS secret...')
    auth_details = subprocess.check_output(
        'az ad sp create-for-rbac --name {} --role contributor --sdk-auth -o json'.format(app_name),
        shell=True)
    auth_details_json = json.loads(auth_details)
    print('')
    print('Name: AZURE_CREDENTIALS')
    print('Value:')
    print(json.dumps(auth_details_json, indent=2))
    _azure_creds_user_choice = prompt(msg='Set the secret in the repository and press enter to continue.')
