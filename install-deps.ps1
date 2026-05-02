$env:PATH = "C:\node-v20.18.0-win-x64;C:\Program Files\Git\bin;C:\Program Files\Git\cmd;" + $env:PATH
Write-Output "PATH updated: $env:PATH"
Write-Output "Node version: $(& node --version)"
Write-Output "NPM version: $(& npm --version)"

Write-Output "Installing frontend dependencies..."
& npm --prefix C:\Users\10517\WorkBuddy\20260429105535\crm-frontend install --legacy-peer-deps 2>&1 | Select-Object -Last 15
Write-Output "Done!"
