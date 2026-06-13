# MoReng Subtitle Maker 랜딩페이지 문구 초안

이 문서는 나중에 `suhoahbi-ui/moreng` 저장소의 랜딩페이지 또는 별도 상세 페이지에 옮겨 붙이기 위한 문구 초안입니다. 이 저장소에서는 실제 모랭 웹사이트를 수정하지 않습니다.

## 추천 URL

- `/moreng/subtitle-maker`
- 또는 `/tools/moreng-subtitle-maker`

## 기존 모랭 랜딩페이지 확장 도구 카드

### 제목

MoReng Subtitle Maker

### 설명

MP4/MP3 파일을 SRT/TXT로 변환하고, Gemini API Key로 다국어 자막까지 생성하는 로컬 자막 도구입니다.

### 버튼

- 자세히 보기
- 다운로드

## 새 상세 페이지 구성

### 1. Hero

제목:

MoReng Subtitle Maker

부제:

MP4/MP3를 SRT/TXT로, SRT를 다국어 자막으로

설명:

영상과 오디오를 외부 서버에 업로드하지 않고, 내 PC에서 자막을 생성하는 로컬 도구입니다. 생성된 SRT는 Gemini API Key를 사용해 영어, 일본어, 중국어, 베트남어 자막으로 번역할 수 있습니다.

버튼:

- Windows 버전 다운로드
- GitHub에서 보기

보안 안내:

영상/오디오 파일은 외부 서버로 업로드되지 않습니다. 단, 번역 기능을 사용할 경우 SRT의 자막 텍스트는 Gemini API로 전송됩니다.

### 2. 주요 기능

- MP4/MP3에서 SRT 자막과 TXT 스크립트 생성
- Gemini API Key로 영어/일본어/중국어/베트남어 SRT 번역
- 원본 SRT 번호와 시간 코드 유지
- faster-whisper 기반 로컬 음성 인식
- API Key 마스킹 입력, 저장, 삭제
- ffmpeg 설치 여부 확인과 설치 안내

### 3. 작동 방식

1. MP4 또는 MP3 파일을 선택합니다.
2. 원본 언어와 Whisper 모델을 선택합니다.
3. 자막 생성을 누르면 SRT/TXT 파일이 저장됩니다.
4. Gemini API Key를 입력하고 저장합니다.
5. 원본 SRT와 번역 언어를 선택해 다국어 SRT를 생성합니다.
6. 완성된 SRT를 유튜브, 편집 프로그램, 강의 자료 제작에 활용합니다.

### 4. 설치 전 확인

- Windows PC에서 실행하는 로컬 도구입니다.
- MP4/MP3에서 오디오를 추출하기 위해 ffmpeg가 필요합니다.
- ffmpeg는 앱에 포함되어 있지 않습니다.
- `run_windows.bat` 실행 시 ffmpeg 설치 여부를 확인합니다.
- ffmpeg가 없으면 winget 설치, 다운로드 페이지 열기, 일단 앱 실행 중 선택할 수 있습니다.
- 수동 설치 시 `ffmpeg.exe`와 `ffprobe.exe`를 `tools\ffmpeg\bin\` 폴더에 넣으면 됩니다.

ffmpeg를 직접 포함하지 않는 이유:

- ffmpeg는 LGPL/GPL 라이선스 조건이 적용될 수 있어 직접 포함 배포 시 별도 라이선스 고지와 배포 조건 확인이 필요합니다.
- 사용자가 공식 또는 신뢰 가능한 페이지에서 직접 받도록 안내하면 변조 파일 배포 위험을 줄일 수 있습니다.
- 보안 프로그램이 외부 exe 파일이 포함된 배포판을 의심하는 경우를 줄일 수 있습니다.
- 사용자가 최신 Windows용 ffmpeg를 직접 선택해 설치할 수 있습니다.

다운로드 링크:

- FFmpeg 공식 다운로드 페이지: https://ffmpeg.org/download.html
- Windows용 FFmpeg 빌드: https://www.gyan.dev/ffmpeg/builds/

### 5. Gemini API Key 안내

- Gemini API Key는 사용자가 직접 발급해야 합니다.
- 앱 입력창에 붙여넣으면 비밀번호처럼 마스킹됩니다.
- 저장 후에도 실제 키는 화면에 표시되지 않습니다.
- API Key는 사용자의 PC에 저장됩니다.
- API Key는 머니체크 서버로 전송되지 않습니다.
- 앱에는 머니체크의 공용 Gemini API Key가 들어있지 않습니다.
- 번역 기능을 사용할 때 SRT의 자막 텍스트는 Gemini API로 전송됩니다.
- Gemini API 사용량, 요금, 제한, 오류, 번역 품질에 대한 책임은 사용자에게 있습니다.
- 사용자는 언제든지 저장된 API Key를 삭제할 수 있습니다.

### 6. 주의사항

- 저작권 있는 영상/음성 사용 가능 여부는 사용자가 직접 확인해야 합니다.
- Gemini API 사용량과 요금은 사용자의 Google/Gemini 계정 정책에 따릅니다.
- 자동 생성 자막과 자동 번역 결과는 검토 후 사용하는 것을 권장합니다.
- ffmpeg는 사용자가 직접 설치해야 합니다.
- 영상에 자막을 입힌 MP4 렌더링, 쇼츠 자동 편집, 로그인/결제 기능은 현재 버전에 포함되어 있지 않습니다.

### 7. 문의

moneychecktruck@gmail.com

