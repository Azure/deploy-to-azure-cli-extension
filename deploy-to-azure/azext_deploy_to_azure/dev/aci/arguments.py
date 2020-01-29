# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def load_aci_arguments(self, _):
    with self.argument_context('aci up') as c:
        c.argument('repository', options_list=['--repository'])
