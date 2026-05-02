$ErrorActionPreference = 'Stop'
$port = 8080
$endpoints = @()
try {
    $endpoints = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue | Select-Object OwningProcess -ExpandProperty OwningProcess
} catch {}
foreach ($pid in $endpoints) {
    Write-Host "Killing PID $pid"
    Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
}
Start-Sleep -Seconds 3
Write-Host "Starting new backend..."
$proc = Start-Process -FilePath "C:\Users\10517\.workbuddy\binaries\python\versions\3.13.12\python.exe" -ArgumentList "C:\Users\10517\WorkBuddy\20260429105535\backend\main.py" -WorkingDirectory "C:\Users\10517\WorkBuddy\20260429105535" -PassThru -RedirectStandardError "C:\Users\10517\WorkBuddy\20260429105535\backend_restart.log"
Write-Host "Started PID: $($proc.Id)"
Start-Sleep -Seconds 5
$check = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue | Select-Object OwningProcess -ExpandProperty OwningProcess
Write-Host "Port $port now owned by PID(s): $check"
