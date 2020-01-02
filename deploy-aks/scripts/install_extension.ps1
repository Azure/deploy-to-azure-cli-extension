python .\setup.py bdist_wheel

az extension remove -n aks-deploy

az extension add --source 'D:\VSTS\AKS_CLI\myAksUpRepo\cli-extension-aks-up\deploy-aks\dist\aks_deploy-0.0.2-py2.py3-none-any.whl' -y