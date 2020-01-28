# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps


def load_aks_help():
    helps['aks app'] = """
    type: group
    short-summary: Commands to manage AKS app.
    long-summary:
    """

    helps['aks app up'] = """
    type: command
    short-summary: Deploy to AKS via GitHub actions.
    long-summary:
    """
