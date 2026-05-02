$python = "C:\Users\10517\.workbuddy\binaries\python\versions\3.13.12\python.exe"
$proj = Join-Path $PSScriptRoot "backend"
Set-Location $proj

Write-Output "Starting backend server..."
& $python main.py 2>&1