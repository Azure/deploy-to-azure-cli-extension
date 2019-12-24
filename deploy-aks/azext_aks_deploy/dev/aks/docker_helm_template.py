# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
from os.path import dirname, abspath
from knack.log import get_logger
from knack.util import CLIError
from azext_aks_deploy.dev.common.const import (APP_NAME_DEFAULT, APP_NAME_PLACEHOLDER,ACR_PLACEHOLDER)
from azext_aks_deploy.dev.common.github_api_helper import Files\

logger = get_logger(__name__)
PACKS_ROOT_STRING = os.path.sep+'resources'+os.path.sep+'packs'+os.path.sep
FILE_ABSOLUTE_PATH = abspath(dirname(dirname(abspath(__file__))))


def get_docker_templates(language):	
    files = []
    language_packs_path = get_supported_language_packs_path(language)	
    if language_packs_path:
        docker_file_path = r'Dockerfile'
        file_path = FILE_ABSOLUTE_PATH + language_packs_path + docker_file_path	
        docker_file_content = get_file_content(file_path)	
        docker_file = Files(path=docker_file_path,content=docker_file_content)	
        logger.debug("Checkin file path: {}".format(docker_file.path))	
        logger.debug("Checkin file content: {}".format(docker_file.content))	
        files.append(docker_file)

        docker_ignore_path = r'.dockerignore'
        file_path = FILE_ABSOLUTE_PATH + language_packs_path + docker_ignore_path	
        docker_ignore_content = get_file_content(file_path)	
        docker_ignore = Files(path=docker_ignore_path,content=docker_ignore_content)	
        logger.debug("Checkin file path: {}".format(docker_ignore.path))	
        logger.debug("Checkin file content: {}".format(docker_ignore.content))	
        files.append(docker_ignore)
    return files

    
def get_helm_charts(language, acr_details):
    language_packs_path = get_supported_language_packs_path(language)
    files = []
    if language_packs_path:
        try:
            abs_pack_path = FILE_ABSOLUTE_PATH+language_packs_path
            # r=root, d=directories, f = files
            for r, d,f in os.walk(abs_pack_path):
                if 'charts' in r:
                    for file in f:
                        if '__pycache__' not in r and '__init__.py' not in file:
                            file_path = os.path.join(r, file)
                            file_content = get_file_content(file_path)
                            # replace values in charts
                            if('values.yaml' in file_path):
                                file_content = replace_values(file_content, acr_details)
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


def get_file_content(path):	
    try:	
        filecontent=open(path).read()	
        return filecontent	
    except Exception as ex:	
        raise CLIError(ex)

def replace_values(file_content, acr_details):
    content=file_content.replace(APP_NAME_PLACEHOLDER, APP_NAME_DEFAULT).replace(ACR_PLACEHOLDER, acr_details['name'])
    return content

def get_supported_language_packs_path(language):
    return (PACKS_ROOT_STRING + language.lower() + os.path.sep)
    
    
