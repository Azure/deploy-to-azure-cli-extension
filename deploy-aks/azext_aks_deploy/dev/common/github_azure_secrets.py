# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.log import get_logger
from knack.util import CLIError
from azext_aks_deploy.dev.common.prompting import prompt_user_friendly_choice_list
from azext_aks_deploy.dev.common.azure_cli_resources import get_default_subscription_info

logger = get_logger(__name__)


def get_azure_credentials():
    import subprocess
    import json
    subscription_id, subscription_name, tenant_id, environment_name = get_default_subscription_info()
    logger.warning("Using your default Azure subscription %s for fetching service prinicipal details.", subscription_name)
    azure_creds_user_choice = 1
    while azure_creds_user_choice == 1:
        print('')
        print('Creating Azure credentials which needs to be stored in Github Secrets of the repo.' )
        print('Please go to to your Github repo page-> Settings ->  Secrets -> Add a new secret')
        print('Enter `AZURE_CREDENTIALS` in the Name field and in the value field, copy/paste the json on the screen. Then, click on `Add Secret`')
        auth_details = subprocess.check_output('az ad sp create-for-rbac --sdk-auth -o json', shell=True)
        auth_details_json = json.loads(auth_details)
        print('')
        print(json.dumps(auth_details_json, indent=2))
        print('')
        user_choice_list = []
        user_choice_list.append('Continue to next key-value pair')
        user_choice_list.append('Re-generate json for AZURE_CREDENTIALS and start-over')
        azure_creds_user_choice = prompt_user_friendly_choice_list(
            'Do you want to:', user_choice_list)

        if azure_creds_user_choice == 0:
            sp_details = subprocess.check_output('az ad sp create-for-rbac -o json' , shell=True)
            sp_details_json = json.loads(sp_details)
            print('Click the `Add a new secret` button')
            print('Enter `REGISTRY_USERNAME` as the key and copy/paste the username GUID displayed on the screen for value.')
            print('')
            print('REGISTRY_USERNAME')
            print(sp_details_json['appId'])
            print('')
            print('Enter `REGISTRY_PASSWORD` as the key and copy/paste the password GUID displayed on the screen for value.')
            print('')
            print('REGISTRY_PASSWORD')
            print(sp_details_json['password'])
            print('')
            azure_creds_user_choice = prompt_user_friendly_choice_list(             
            'Do you want to:', ['Continue','Re-generate json for AZURE_CREDENTIALS and start-over'])
    return
