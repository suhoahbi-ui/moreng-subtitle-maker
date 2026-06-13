@echo off
chcp 65001 > nul
setlocal
cd /d "%~dp0"

echo MoReng Subtitle Maker - ffmpeg 설치 후 실행
echo.

where winget > nul 2> nul
if errorlevel 1 (
  echo winget을 찾을 수 없습니다.
  echo 설치전_필독.txt를 읽고 ffmpeg를 수동 설치하거나 tools\ffmpeg\bin 폴더에 넣어주세요.
  pause
  exit /b 1
)

winget install --id Gyan.FFmpeg -e
echo.
echo 설치가 끝났습니다.
echo 현재 창에 PATH가 바로 반영되지 않을 수 있으니, run_windows.bat가 실패하면 창을 닫고 다시 실행해주세요.
echo.
call "%~dp0run_windows.bat"
