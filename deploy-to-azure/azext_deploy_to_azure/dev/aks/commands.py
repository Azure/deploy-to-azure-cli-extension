# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands import CliCommandType

aksops = CliCommandType(
    operations_tmpl='azext_deploy_to_azure.dev.aks.up#{}'
)


def load_aks_commands(self, _):
    with self.command_group('aks app', command_type=aksops, is_preview=True) as g:
        g.command('up', 'aks_deploy')
