@echo off
chcp 65001 > nul
setlocal
cd /d "%~dp0"

echo MoReng Subtitle Maker
echo 설치 안내는 설치전_필독.txt를 확인해주세요.
echo.

call :CheckFfmpeg
if "%FFMPEG_READY%"=="0" (
  echo.
  echo [필수 확인] ffmpeg 또는 ffprobe를 찾을 수 없습니다.
  echo MP4/MP3에서 오디오를 추출하려면 ffmpeg가 필요합니다.
  echo.
  echo 선택:
  echo   1. winget으로 ffmpeg 설치 후 계속
  echo   2. 다운로드 페이지 열기
  echo   3. 일단 앱 실행
  echo.
  set /p "FFMPEG_CHOICE=번호를 입력하세요 [1/2/3]: "

  if "%FFMPEG_CHOICE%"=="1" (
    where winget > nul 2> nul
    if errorlevel 1 (
      echo.
      echo winget을 찾을 수 없습니다. 설치전_필독.txt를 읽고 수동 설치해주세요.
      pause
      exit /b 1
    )

    winget install --id Gyan.FFmpeg -e
    call :CheckFfmpeg
    if "%FFMPEG_READY%"=="0" (
      echo.
      echo 설치가 끝났지만 현재 창에는 PATH가 아직 반영되지 않았을 수 있습니다.
      echo 이 창을 닫고 run_windows.bat를 다시 실행해주세요.
      pause
      exit /b 1
    )
  ) else if "%FFMPEG_CHOICE%"=="2" (
    start "" "https://www.gyan.dev/ffmpeg/builds/"
    echo.
    echo FFmpeg 공식 다운로드 페이지:
    echo https://ffmpeg.org/download.html
    echo.
    echo Windows용 FFmpeg 빌드:
    echo https://www.gyan.dev/ffmpeg/builds/
    echo.
    echo FFmpeg 압축 파일에서 ffmpeg.exe와 ffprobe.exe를 찾아 아래 폴더에 넣어주세요.
    echo %~dp0tools\ffmpeg\bin\
    echo.
    pause
    exit /b 1
  ) else (
    echo.
    echo ffmpeg 없이 실행합니다. 자막 생성 기능은 실패할 수 있습니다.
  )
)

if not exist ".venv\Scripts\python.exe" (
  py -3 -m venv .venv
)

call ".venv\Scripts\activate.bat"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python app.py

pause
exit /b 0

:CheckFfmpeg
set "FFMPEG_READY=0"

if exist "%~dp0tools\ffmpeg\bin\ffmpeg.exe" (
  if exist "%~dp0tools\ffmpeg\bin\ffprobe.exe" (
    set "FFMPEG_READY=1"
  )
)

if "%FFMPEG_READY%"=="0" (
  if exist "%~dp0ffmpeg.exe" (
    if exist "%~dp0ffprobe.exe" (
      set "FFMPEG_READY=1"
    )
  )
)

if "%FFMPEG_READY%"=="0" (
  where ffmpeg > nul 2> nul
  if not errorlevel 1 (
    where ffprobe > nul 2> nul
    if not errorlevel 1 (
      set "FFMPEG_READY=1"
    )
  )
)

exit /b 0
