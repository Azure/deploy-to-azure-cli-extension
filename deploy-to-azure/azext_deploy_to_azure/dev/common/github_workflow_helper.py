
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError
from knack.log import get_logger

from azext_deploy_to_azure.dev.common.github_api_helper import get_check_run_status_and_conclusion
from azext_deploy_to_azure.dev.common.prompting import prompt_not_empty

logger = get_logger(__name__)


def poll_workflow_status(repo_name, check_run_id):
    import colorama
    import humanfriendly
    import time
    check_run_status = None
    check_run_status, check_run_conclusion = get_check_run_status_and_conclusion(repo_name, check_run_id)
    if check_run_status == 'queued':
        # When workflow status is Queued
        colorama.init()
        with humanfriendly.Spinner(label="Workflow is in queue") as spinner:  # pylint: disable=no-member
            while True:
                spinner.step()
                time.sleep(0.5)
                check_run_status, check_run_conclusion = get_check_run_status_and_conclusion(repo_name, check_run_id)
                if check_run_status in ('in_progress', 'completed'):
                    break
        colorama.deinit()
    if check_run_status == 'in_progress':
        # When workflow status is inprogress
        colorama.init()
        with humanfriendly.Spinner(label="Workflow is in progress") as spinner:  # pylint: disable=no-member
            while True:
                spinner.step()
                time.sleep(0.5)
                check_run_status, check_run_conclusion = get_check_run_status_and_conclusion(repo_name, check_run_id)
                if check_run_status == 'completed':
                    break
        colorama.deinit()
    print('GitHub workflow completed.')
    if check_run_conclusion == 'success':
        print('Workflow succeeded')
    else:
        raise CLIError('Workflow status: {}'.format(check_run_conclusion))


def get_new_workflow_yaml_name():
    logger.warning('A yaml file main.yml already exists in the .github/workflows folder.')
    new_workflow_yml_name = prompt_not_empty(
        msg='Enter a new name for workflow yml file: ',
        help_string='e.g. /new_main.yml to add in the .github/workflows folder.')
    return new_workflow_yml_name
