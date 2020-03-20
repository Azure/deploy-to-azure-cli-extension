# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps


def load_aci_help():
    helps['container app'] = """
    type: group
    short-summary: Commands to Manage Azure Container Instances App
    long-summary:
    """

    helps['container app up'] = """
    type: command
    short-summary: Deploy to Azure Container Instances using GitHub Actions. Refer https://aka.ms/aci-deploy-action for more information. 
    long-summary:
    """
