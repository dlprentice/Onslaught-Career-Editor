@echo off
setlocal
set "SCRIPT_ROOT=%~dp0"
where pwsh.exe >nul 2>&1
if errorlevel 1 (
  echo First Flight requires PowerShell 7 ^(pwsh^).
  echo Install PowerShell 7, then run this launcher again.
  pause
  exit /b 1
)
pwsh.exe -NoLogo -NoProfile -File "%SCRIPT_ROOT%tools\Run-FirstFlight.ps1" %*
if errorlevel 1 (
  echo.
  echo First Flight could not start. Review the error above.
  pause
)
endlocal
