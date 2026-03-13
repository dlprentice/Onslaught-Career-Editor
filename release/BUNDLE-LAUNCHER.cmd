@echo off
setlocal

set "APP_EXE=%~dp0app\OnslaughtCareerEditor.WinUI.exe"

if not exist "%APP_EXE%" (
    echo Could not find the portable app at:
    echo   "%APP_EXE%"
    exit /b 1
)

start "" "%APP_EXE%" %*
