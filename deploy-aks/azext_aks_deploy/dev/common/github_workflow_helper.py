
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

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
    if check_run_conclusion == 'success':
        print('Workflow succeeded')
    else:
        raise CLIError('Workflow status: {}'.format(check_run_conclusion))