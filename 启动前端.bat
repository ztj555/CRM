@echo off
chcp 65001 >nul
title 融鑫CRM - 前端服务
echo ====================================
echo  融鑫CRM 前端服务  (端口 5173)
echo ====================================
echo.

cd /d "%~dp0crm-frontend"
"C:\node-v20.18.0-win-x64\node.exe" "C:\node-v20.18.0-win-x64\node_modules\npm\bin\npm-cli.js" run dev

pause
