@echo off
setlocal
cd /d "%~dp0"

echo MoReng Subtitle Maker
echo Please read README.md and the Korean setup note before use.
echo.

call :CheckFfmpeg
if "%FFMPEG_READY%"=="1" goto StartApp
goto MissingFfmpeg

:MissingFfmpeg
echo.
echo [Required] ffmpeg or ffprobe was not found.
echo ffmpeg is required to extract audio from MP4/MP3 files.
echo.
echo Choose:
echo   1. Install ffmpeg with winget, then continue
echo   2. Open the ffmpeg download page
echo   3. Run the app anyway
echo.
set "FFMPEG_CHOICE="
set /p "FFMPEG_CHOICE=Enter a number [1/2/3]: "

if "%FFMPEG_CHOICE%"=="1" goto InstallFfmpeg
if "%FFMPEG_CHOICE%"=="2" goto OpenFfmpegDownload
goto StartWithoutFfmpeg

:InstallFfmpeg
where winget > nul 2> nul
if errorlevel 1 goto WingetMissing

winget install --id Gyan.FFmpeg -e
call :CheckFfmpeg
if "%FFMPEG_READY%"=="1" goto StartApp

echo.
echo ffmpeg may have been installed, but PATH may not be refreshed yet.
echo Close this window and run run_windows.bat again.
pause
exit /b 1

:WingetMissing
echo.
echo winget was not found.
echo Please install ffmpeg manually or place ffmpeg.exe and ffprobe.exe under:
echo %~dp0tools\ffmpeg\bin\
pause
exit /b 1

:OpenFfmpegDownload
start "" "https://www.gyan.dev/ffmpeg/builds/"
echo.
echo FFmpeg official download page:
echo https://ffmpeg.org/download.html
echo.
echo Windows FFmpeg builds:
echo https://www.gyan.dev/ffmpeg/builds/
echo.
echo Recommended file: release builds - ffmpeg-release-essentials.zip
echo Do not choose tools.zip, full-shared, or source code for normal use.
echo.
echo Place ffmpeg.exe and ffprobe.exe under:
echo %~dp0tools\ffmpeg\bin\
echo.
pause
exit /b 1

:StartWithoutFfmpeg
echo.
echo Running without ffmpeg. Subtitle generation may fail until ffmpeg is installed.
goto StartApp

:StartApp
if exist ".venv\Scripts\python.exe" goto VenvReady

echo.
echo Creating Python virtual environment...
py -3 -m venv .venv
if errorlevel 1 goto VenvFailed

:VenvReady
if exist ".venv\Scripts\activate.bat" goto ActivateVenv
goto VenvFailed

:ActivateVenv
call ".venv\Scripts\activate.bat"

python -m pip install --upgrade pip
if errorlevel 1 goto PipFailed

python -m pip install -r requirements.txt
if errorlevel 1 goto PipFailed

python app.py
if errorlevel 1 goto AppFailed

pause
exit /b 0

:VenvFailed
echo.
echo Could not create the Python virtual environment.
echo Please check that Python 3.10 or newer is installed.
pause
exit /b 1

:PipFailed
echo.
echo Could not install required Python packages.
echo Please check your internet connection and Python installation.
pause
exit /b 1

:AppFailed
echo.
echo The app exited with an error.
pause
exit /b 1

:CheckFfmpeg
set "FFMPEG_READY=0"

if exist "%~dp0tools\ffmpeg\bin\ffmpeg.exe" if exist "%~dp0tools\ffmpeg\bin\ffprobe.exe" set "FFMPEG_READY=1"
if "%FFMPEG_READY%"=="1" exit /b 0

if exist "%~dp0ffmpeg.exe" if exist "%~dp0ffprobe.exe" set "FFMPEG_READY=1"
if "%FFMPEG_READY%"=="1" exit /b 0

where ffmpeg > nul 2> nul
if errorlevel 1 exit /b 0

where ffprobe > nul 2> nul
if errorlevel 1 exit /b 0

set "FFMPEG_READY=1"
exit /b 0
