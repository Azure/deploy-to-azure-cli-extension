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

    
def get_docker_and_helm_charts(languages):
    language_packs_path = get_supported_language_packs_path(languages)
    files = []
    if language_packs_path:
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
        except Exception as ex:
            raise CLIError(ex)
    return files


def get_supported_language_packs_path(languages):
    language = choose_supported_language(languages)
    if language:
        return (PACKS_ROOT_STRING + language.lower() + os.path.sep)
    
    
def choose_supported_language(languages):
    list_languages = list(languages.keys())
    first_language = list_languages[0]
    if 'JavaScript' == first_language or 'Java' == first_language or 'Python' == first_language:
        return first_language
    elif len(list_languages) >= 1 and ( 'JavaScript' == list_languages[1] or 'Java' == list_languages[1] or 'Python' == list_languages[1]):
        return list_languages[1]
    return None

