# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
from knack.log import get_logger
from knack.util import CLIError
from azext_aks_deploy.dev.common.github_api_helper import Files\

logger = get_logger(__name__)
PACKS_ROOT_STRING = os.path.sep+'packs'+os.path.sep
FILE_ABSOLUTE_PATH = os.path.abspath(os.path.dirname(__file__))

    
def get_docker_and_helm_charts(language):
    language_packs_path = get_supported_language_packs_path(language)
    files = []
    try:
        abs_pack_path = FILE_ABSOLUTE_PATH+language_packs_path
        # r=root, d=directories, f = files
        for r, d,f in os.walk(abs_pack_path):
            for file in f:
                if '__pycache__' not in r and '__init__.py' not in file:
                    file_path = os.path.join(r, file)
                    file_content = open(file_path).read()
                    if file_path.startswith(abs_pack_path):
                        file_path=file_path[len(abs_pack_path):]
                        file_path = file_path.replace('\\','/')
                    file_obj = Files(path=file_path,content=file_content)
                    logger.debug("Checkin file path: {}".format(file_path))
                    logger.debug("Checkin file content: {}".format(file_content))
                    files.append(file_obj)
        return files
    except Exception as ex:
        raise CLIError(ex)


def get_supported_language_packs_path(language):
    LANGUAGE_PACKS_PATH = PACKS_ROOT_STRING + language.lower() + os.path.sep
    if 'JavaScript' == language or 'Java' == language or 'Python' == language:
        return LANGUAGE_PACKS_PATH
    raise CLIError("Docker file and helm charts templates are only supported for Javascript , Java and Python languages."
                    "Please commit your Dockerfile and helm charts into the repo and run the 'az aks up'command again")
