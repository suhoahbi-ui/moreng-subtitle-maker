# MoReng Subtitle Maker v0.1.0

MoReng Subtitle Maker는 Windows PC에서 MP4/MP3 파일을 SRT/TXT로 변환하고, Gemini API Key로 다국어 SRT 자막을 생성하는 로컬 자막 도구입니다.

릴리스 정보:

- Product: MoReng Subtitle Maker / 모랭 자막 메이커
- Created by: MoneyCheck / 머니체크
- GitHub: https://github.com/suhoahbi-ui/moreng-subtitle-maker
- Contact: moneychecktruck@gmail.com

이번 릴리스는 exe 설치 프로그램이 아니라 ZIP 배포판입니다. ZIP 파일을 다운로드하고 압축을 푼 뒤 `run_windows.bat`를 더블클릭해 실행할 수 있습니다.

## 주요 기능

- MP4/MP3 파일에서 SRT 자막 생성
- 전체 스크립트 TXT 파일 생성
- 원본 언어 선택: 자동감지, 한국어, 영어, 일본어, 중국어
- Whisper 모델 선택: `small`, `medium`, `large-v3`
- faster-whisper 기반 로컬 음성 인식
- Gemini API Key 마스킹 입력, 저장, 삭제
- 영어/일본어/중국어/베트남어 SRT 번역
- 원본 SRT 번호와 시간 코드 유지
- 진행 상태와 사용자용 로그 표시

## 설치 방법

1. `MoReng-Subtitle-Maker-v0.1.0-windows.zip`을 다운로드합니다.
2. 원하는 폴더에 압축을 풉니다.
3. 압축을 푼 폴더 안의 `설치전_필독.txt`를 먼저 읽습니다.
4. `run_windows.bat`를 더블클릭합니다.
5. 첫 실행 시 Python 가상환경과 필요한 패키지가 설치됩니다.

Python 3.10 이상을 권장합니다.

## ffmpeg 안내

이 앱은 MP4/MP3에서 오디오를 추출하기 위해 ffmpeg와 ffprobe가 필요합니다.

ffmpeg는 ZIP 파일에 포함되어 있지 않습니다. `run_windows.bat` 실행 시 ffmpeg 설치 여부를 확인하고, 없으면 아래 선택지를 보여줍니다.

```text
1. winget으로 ffmpeg 설치 후 계속
2. 다운로드 페이지 열기
3. 일단 앱 실행
```

ffmpeg를 앱에 직접 포함하지 않는 이유:

- ffmpeg는 LGPL/GPL 라이선스 조건이 적용될 수 있어 직접 포함 배포 시 별도 라이선스 고지와 배포 조건 확인이 필요합니다.
- 사용자가 공식 또는 신뢰 가능한 페이지에서 직접 받도록 안내하면 변조 파일 배포 위험을 줄일 수 있습니다.
- 보안 프로그램이 외부 exe 파일이 포함된 배포판을 의심하는 경우를 줄일 수 있습니다.
- 사용자가 최신 Windows용 ffmpeg를 직접 선택해 설치할 수 있습니다.

참고 링크:

- FFmpeg 공식 다운로드 페이지: https://ffmpeg.org/download.html
- Windows용 FFmpeg 빌드: https://www.gyan.dev/ffmpeg/builds/

수동 설치를 선택한 경우 gyan.dev 페이지의 `release builds` 섹션에서 `ffmpeg-release-essentials.zip`을 받는 것을 권장합니다.

- `ffmpeg-release-essentials.zip`: 일반 사용자 권장
- `ffmpeg-release-essentials.7z`: 7-Zip이 있다면 선택 가능
- `ffmpeg-release-full.7z`, `full-shared.7z`, `git` 빌드, `tools.zip`: 이 앱에는 보통 필요하지 않음

압축을 푼 뒤 `bin` 폴더 안의 `ffmpeg.exe`와 `ffprobe.exe`를 아래 폴더에 넣으면 앱에서 사용할 수 있습니다.

```text
tools\ffmpeg\bin\
```

## Gemini API Key 안내

- Gemini API Key는 사용자가 직접 발급해야 합니다.
- 앱에는 머니체크의 공용 Gemini API Key가 들어있지 않습니다.
- API Key는 사용자의 PC에 저장됩니다.
- API Key는 머니체크 서버로 전송되지 않습니다.
- 입력창과 저장 상태에서는 실제 키가 평문으로 보이지 않습니다.
- 사용자는 언제든지 저장된 API Key를 삭제할 수 있습니다.
- Gemini API 사용량, 요금, 제한, 오류, 번역 품질에 대한 책임은 사용자에게 있습니다.

## 개인정보와 외부 전송 범위

영상/오디오 파일은 외부 서버로 업로드되지 않습니다. 음성 인식은 사용자의 PC에서 로컬로 실행됩니다.

단, 번역 기능을 사용할 경우 SRT의 자막 텍스트는 Gemini API로 전송됩니다.

## 알려진 제한사항

- Windows 로컬 실행을 우선 지원합니다.
- exe 설치 프로그램은 아직 제공하지 않습니다.
- ffmpeg는 사용자가 직접 설치해야 합니다.
- 처음 실행 시 Python 패키지와 Whisper 모델 다운로드가 필요할 수 있습니다.
- 영상에 자막을 입힌 MP4 렌더링 기능은 아직 포함되어 있지 않습니다.
- 쇼츠 자동 편집, 로그인, 회원가입, 결제 기능은 포함되어 있지 않습니다.
- 자동 생성 자막과 자동 번역 결과는 검토 후 사용하는 것을 권장합니다.

## 문의

moneychecktruck@gmail.com
