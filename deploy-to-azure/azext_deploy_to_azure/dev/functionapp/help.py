# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps


def load_functionapp_help():
    helps['functionapp app'] = """
    type: group
    short-summary: Commands to manage Azure Functions app.
    long-summary:
    """

    helps['functionapp app up'] = """
    type: command
    short-summary: Deploy to Azure Functions via GitHub actions.
    long-summary:
    examples:
      - name: Deploy/Setup GitHub action for a GitHub Repository to Azure Function - Run interactive mode
        text: |
          az functionapp app up

      - name: Deploy/Setup GitHub Action for locally checked out GitHub Repository to Azure Function
        text: |
          Repository name/url (--repository) will be detected from the local git repository
          az functionapp app up --app-name AzFunctionPythonPreProd

      - name: Deploy/Setup GitHub action for a GitHub Repository to Azure Function
        text: |
          az functionapp app up --app-name AzFunctionPythonPreProd --repository https://github.com/azure/deploy-functions
    """
