$env:PATH = "C:\node-v20.18.0-win-x64;" + $env:PATH
$proj = Join-Path $PSScriptRoot "crm-frontend"
Set-Location $proj
Write-Output "Working in: $proj"
Write-Output "Node: $(& node --version)"
Write-Output "npm: $(& npm --version)"

Write-Output "Installing dependencies..."
& npm.cmd install --legacy-peer-deps 2>&1 | Select-Object -Last 20
Write-Output "Done!"
