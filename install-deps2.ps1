$env:PATH = "C:\node-v20.18.0-win-x64;" + $env:PATH
Write-Output "Node: $(& node --version 2>&1)"

$proj = Join-Path $PSScriptRoot "crm-frontend"
Write-Output "Project path: $proj"
Write-Output "Contents: $(Get-ChildItem $proj | Select-Object -First 5 Name)"

Write-Output "Installing..."
& npm.cmd --prefix $proj install --legacy-peer-deps 2>&1 | Select-Object -Last 20
Write-Output "Done!"
