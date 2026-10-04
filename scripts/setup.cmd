@echo off
rem Automated setup for Windows: runs setup.ps1 next to this file.
rem This file is ASCII-only on purpose: cmd.exe reads .cmd files in the OEM code page,
rem so Thai UTF-8 text here could be misread. Thai help text lives in setup.ps1.
rem -ExecutionPolicy Bypass applies to this run only; the machine policy is not changed.
rem Usage: scripts\setup.cmd [-Clean] [-Seed] [-SkipTests]
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup.ps1" %*
exit /b %ERRORLEVEL%
