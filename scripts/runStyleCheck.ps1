$failure = $false             

Write-Output "Installing pylint"
python -m pip install --user pylint

Write-Output "Installing flake8"
python -m pip install --user flake8

Write-Output "Running pylint on all source"
python -m pylint --rcfile pylintrc ./deploy-to-azure/azext_aks_deploy -f colorized

if ($LastExitCode -ne 0) {
    $failure = $true
    Write-Output "Pylint NOT OK!"
  } else {
    Write-Output "Pylint OK!"
  }

Write-Output "Running flake8 checks"
python -m  flake8 --config .flake8

if ($LastExitCode -ne 0) {
    $failure = $true
    Write-Output "flake8 NOT OK!"
  } else {
    Write-Output "flake8 OK!"
  }

if($failure -eq $true){
    exit 1
}