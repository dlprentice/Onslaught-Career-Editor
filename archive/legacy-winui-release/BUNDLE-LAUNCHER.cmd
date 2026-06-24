@echo off
setlocal

set "APP_EXE=%~dp0app\OnslaughtCareerEditor.WinUI.exe"
echo SUPERSEDED: legacy WinUI bundle only. WinUI 3 is the active product lane; Electron is archived/reference.

if not exist "%APP_EXE%" (
    echo Could not find the portable app at:
    echo   "%APP_EXE%"
    exit /b 1
)

start "" "%APP_EXE%" %*
