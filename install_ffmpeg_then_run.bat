@echo off
setlocal
cd /d "%~dp0"

echo MoReng Subtitle Maker - install ffmpeg and run
echo.

where winget > nul 2> nul
if errorlevel 1 goto WingetMissing

winget install --id Gyan.FFmpeg -e
if errorlevel 1 goto InstallFailed

echo.
echo ffmpeg installation finished.
echo If run_windows.bat still cannot find ffmpeg, close this window and run it again.
echo.
call "%~dp0run_windows.bat"
exit /b %ERRORLEVEL%

:WingetMissing
echo winget was not found.
echo Please install ffmpeg manually or place ffmpeg.exe and ffprobe.exe under:
echo %~dp0tools\ffmpeg\bin\
echo Recommended manual download: release builds - ffmpeg-release-essentials.zip
pause
exit /b 1

:InstallFailed
echo.
echo ffmpeg installation failed.
echo Please read README.md and try manual installation.
pause
exit /b 1
