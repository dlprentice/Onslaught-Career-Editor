@echo off
setlocal

set "ELECTRON_EXE=%~dp0runtime\electron\electron.exe"
set "APP_ROOT=%~dp0app"

if not exist "%ELECTRON_EXE%" (
    echo Could not find the bundled Electron runtime at:
    echo   "%ELECTRON_EXE%"
    exit /b 1
)

if not exist "%APP_ROOT%\package.json" (
    echo Could not find the bundled Onslaught Workbench app at:
    echo   "%APP_ROOT%"
    exit /b 1
)

start "" "%ELECTRON_EXE%" "%APP_ROOT%" %*
