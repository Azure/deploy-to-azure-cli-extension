# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader
from knack.events import EVENT_INVOKER_POST_PARSE_ARGS


class DevCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        custom_type = CliCommandType(operations_tmpl='azext_aks_deploy#{}')
        super(DevCommandsLoader, self).__init__(cli_ctx=cli_ctx,
                                                custom_command_type=custom_type)

    def load_command_table(self, args):
        from azext_aks_deploy.dev.aks.commands import load_aks_commands
        from azext_aks_deploy.dev.functionapp.commands import load_functionapp_commands
        load_aks_commands(self, args)
        load_functionapp_commands(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_aks_deploy.dev.aks.arguments import load_aks_arguments
        from azext_aks_deploy.dev.functionapp.arguments import load_functionapp_arguments
        load_aks_arguments(self, command)
        load_functionapp_arguments(self, command)

COMMAND_LOADER_CLS = DevCommandsLoader
