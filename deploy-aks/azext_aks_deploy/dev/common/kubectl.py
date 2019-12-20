# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from knack.log import get_logger
from knack.util import CLIError
from azext_aks_deploy.dev.common.utils import which

logger = get_logger(__name__)

def get_deployment_IP_port(app_name):
    if not which('kubectl'):
        raise CLIError('Can not find kubectl executable in PATH')
    try:
        import subprocess
        import json
        service_details = subprocess.check_output('kubectl get service {} -o json'.format(app_name), shell=True)
        service_obj = json.loads(service_details)
        deployment_ip = service_obj['status']['loadBalancer']['ingress'][0]['ip']
        port = service_obj['spec']['ports'][0]['port']
        return deployment_ip,port
    except subprocess.CalledProcessError as err:
        raise CLIError('Could not find app/service: {}'.format(err))