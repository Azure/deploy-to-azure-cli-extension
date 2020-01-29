# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps


def load_aci_help():
    helps['aci'] = """
    type: group
    short-summary: Commands to Manage Azure Container Instances App
    long-summary:
    """

    helps['aci up'] = """
    type: command
    short-summary: Deploy to Azure Container Instances using GitHub Actions
    long-summary:
    """
