# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from knack.log import get_logger
from knack.util import CLIError
from azure.cli.core.extension import get_extension_path
from azure.cli.core.extension.operations import _run_pip

PYPERCLIP_MSG = """
Pyperclip could not find a copy/paste mechanism for your system.
On Linux, install xclip or xsel via package manager. For example, in Debian:
    sudo apt-get install xclip
    sudo apt-get install xsel
    
If you're seeing this error on Windows or Mac please visit https://pyperclip.readthedocs.io/en/latest/introduction.html#not-implemented-error
"""
logger = get_logger(__name__)

FILE_ENCODING_TYPES = ['ascii', 'utf-16be', 'utf-16le', 'utf-8']


def read_file_content(file_path, encoding):
    if not file_path or not encoding:
        raise CLIError("File path {} or encoding {} is missing.".format(file_path, encoding))

    if encoding not in FILE_ENCODING_TYPES:
        raise CLIError("File encoding {encoding} is not supported.".format(encoding=encoding))

    try:
        import sys
        if sys.version_info[0] < 3:
            return _read_file_content_ver2(file_path, encoding)

        return _read_file_content_ver3(file_path, encoding)
    except UnicodeDecodeError as ex:
        logger.debug(msg=ex)
        raise CLIError("Unable to decode file '{}' with '{}' encoding.".format(
            file_path, encoding))


def open_file(filepath):
    """
    Opens a file in the default editor for the file type and exits.
    """
    import subprocess
    import platform
    import os
    if platform.system() == 'Darwin':       # macOS
        subprocess.call(('open', filepath))
    elif platform.system() == 'Windows':    # Windows
        os.system(filepath)
    else:                                   # linux variants
        subprocess.call(('xdg-open', filepath))


def delete_dir(path):
    import shutil
    shutil.rmtree(path)


def datetime_now_as_string():
    from datetime import datetime
    now = datetime.utcnow().isoformat()
    return ''.join(e for e in now if e.isalnum())


def open_url(url):
    """Opens the url in new window in the default browser.
    """
    from webbrowser import open_new
    open_new(url=url)


# Decorators
def singleton(myclass):
    instance = [None]

    def wrapper(*args, **kwargs):
        if instance[0] is None:
            instance[0] = myclass(*args, **kwargs)
        return instance[0]
    return wrapper


def copy_to_clipboard(content):
    try:
        import pyperclip
    except ModuleNotFoundError as ex:
        logger.debug(ex)
        _install_package(pyperclip)
    try:
        pyperclip.copy(content)
    except pyperclip.PyperclipException as ex:
        CLIError(PYPERCLIP_MSG)

        
def _install_package(package_name):
    logger.debug('Installing pyperclip')
    extensionPath = get_extension_path('aks-deploy')
    pip_args = ['install' ,package_name, '--target' , extensionPath]
    pip_status_code = _run_pip(pip_args)
    if pip_status_code > 0:
        raise CLIError('An error occurred. Pip failed with status code {} for package {}. '
                       'Use --debug for more information.'.format(pip_status_code, package_name))

def _read_file_content_ver3(file_path, encoding):
    logger.debug('inside read_file_content_ver3')
    with open(file_path, 'r', encoding=encoding) as f:
        return f.read()


def _read_file_content_ver2(file_path, encoding):
    logger.debug('inside read_file_content_ver2')
    with open(file_path) as f:
        return f.read().decode(encoding)
