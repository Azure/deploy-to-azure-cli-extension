# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader


class DevCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        custom_type = CliCommandType(operations_tmpl='azext_deploy_to_azure#{}')
        super(DevCommandsLoader, self).__init__(cli_ctx=cli_ctx,
                                                custom_command_type=custom_type)

    def load_command_table(self, args):
        from azext_deploy_to_azure.dev.aks.commands import load_aks_commands
        from azext_deploy_to_azure.dev.functionapp.commands import load_functionapp_commands
        from azext_deploy_to_azure.dev.aci.commands import load_aci_commands
        load_aks_commands(self, args)
        load_functionapp_commands(self, args)
        load_aci_commands(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_deploy_to_azure.dev.aks.arguments import load_aks_arguments
        from azext_deploy_to_azure.dev.functionapp.arguments import load_functionapp_arguments
        from azext_deploy_to_azure.dev.aci.arguments import load_aci_arguments
        load_aks_arguments(self, command)
        load_functionapp_arguments(self, command)
        load_aci_arguments(self, command)


COMMAND_LOADER_CLS = DevCommandsLoader
