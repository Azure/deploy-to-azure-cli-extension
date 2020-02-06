# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
try:
    # Attempt to load mock (works on Python 3.3 and above)
    from unittest.mock import patch
except ImportError:
    # Attempt to load mock (works on Python version below 3.3)
    from mock import patch
from azext_deploy_to_azure.dev.common.git import is_github_url_candidate


class TestGitMethods(unittest.TestCase):

    def test_github_url_candidate(self):
        self.assertEqual(is_github_url_candidate(url='https://github.com/org/repo'), True)
        self.assertEqual(is_github_url_candidate(url='https://github.com/org/repo/'), True)
        self.assertEqual(is_github_url_candidate(url='https://github.com/org'), True)
        self.assertEqual(is_github_url_candidate(url='https://github.com'), True)
        self.assertEqual(is_github_url_candidate(url='https://dev.azure.com/org'), False)
        self.assertEqual(is_github_url_candidate(url='https://github.in/org/repo'), False)
        self.assertEqual(is_github_url_candidate(url=None), False)
        self.assertEqual(is_github_url_candidate(url='not a url'), False)

if __name__ == '__main__':
    unittest.main() 
