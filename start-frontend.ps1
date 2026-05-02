$env:PATH = "C:\node-v20.18.0-win-x64;" + $env:PATH
$proj = Join-Path $PSScriptRoot "crm-frontend"
Set-Location $proj

Write-Output "Starting frontend dev server..."
& npm.cmd run dev 2>&1