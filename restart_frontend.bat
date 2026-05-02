chcp 65001 >nul
taskkill /F /IM node.exe 2>nul
cd /d %~dp0crm-frontend
start "" /min "%~dp0c:\node-v20.18.0-win-x64\node.exe" node.exe node_modules\vite\bin\vite.js --host 0.0.0.0 --port 5173
timeout /t 3 /nobreak >nul
echo Frontend started
