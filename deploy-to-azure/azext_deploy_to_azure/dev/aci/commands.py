# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands import CliCommandType

aciops = CliCommandType(
    operations_tmpl='azext_deploy_to_azure.dev.aci.up#{}'
)


def load_aci_commands(self, _):
    with self.command_group('aci') as g:
        g.command('up', 'aci_up')
