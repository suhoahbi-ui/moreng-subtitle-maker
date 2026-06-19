from __future__ import annotations

import queue
import tempfile
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from src.audio import extract_audio_to_wav, get_duration_seconds
from src.config import (
    APP_BRAND,
    APP_DESCRIPTION,
    APP_SUBTITLE,
    APP_TITLE,
    CONTACT_EMAIL,
    DEFAULT_SOURCE_LANGUAGE,
    DEFAULT_TARGET_LANGUAGE,
    DEFAULT_WHISPER_MODEL,
    SOURCE_LANGUAGES,
    SUPPORTED_MEDIA_EXTENSIONS,
    TARGET_LANGUAGES,
    GITHUB_URL,
    WHISPER_MODELS,
)
from src.gemini_translator import GeminiTranslator, write_failure_log
from src.key_store import KeyStore
from src.srt_parser import read_srt, save_srt_blocks
from src.srt_writer import write_srt
from src.transcript_writer import write_transcript
from src.utils import normalize_language_code, subtitle_output_paths, translated_srt_output_path
from src.whisper_engine import WhisperEngine


class SubtitleToolApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("980x820")
        self.root.minsize(860, 700)

        self.colors = {
            "bg": "#f6f7f9",
            "card": "#ffffff",
            "border": "#dfe3ea",
            "text": "#171923",
            "muted": "#5f6673",
            "soft": "#edf1f7",
            "primary": "#2563eb",
            "primary_active": "#1d4ed8",
            "success_bg": "#e8f7ef",
            "success": "#166534",
            "warning_bg": "#fff7ed",
            "warning": "#9a3412",
        }

        self.key_store = KeyStore()
        self.events: queue.Queue[tuple[str, object]] = queue.Queue()
        self.last_srt_path: Path | None = None
        self.is_busy = False

        self.media_path_var = tk.StringVar()
        self.srt_path_var = tk.StringVar()
        self.output_dir_var = tk.StringVar()
        self.media_display_var = tk.StringVar(value="선택된 파일 없음")
        self.srt_display_var = tk.StringVar(value="선택된 SRT 없음")
        self.output_display_var = tk.StringVar(value="원본 파일과 같은 폴더")
        self.source_language_var = tk.StringVar(value=DEFAULT_SOURCE_LANGUAGE)
        self.whisper_model_var = tk.StringVar(value=DEFAULT_WHISPER_MODEL)
        self.target_language_var = tk.StringVar(value=DEFAULT_TARGET_LANGUAGE)
        self.key_status_var = tk.StringVar()
        self.stage_var = tk.StringVar(value="대기 중")
        self.progress_var = tk.DoubleVar(value=0.0)
        self.output_paths_var = tk.StringVar(value="저장된 파일이 아직 없습니다.")

        self._configure_styles()
        self._build_ui()
        self._refresh_key_status()
        self.root.after(100, self._poll_events)

    def _configure_styles(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("App.TFrame", background=self.colors["bg"])
        style.configure("Card.TFrame", background=self.colors["card"], relief="flat")
        style.configure("Muted.TLabel", background=self.colors["card"], foreground=self.colors["muted"], font=("맑은 고딕", 9))
        style.configure("Body.TLabel", background=self.colors["card"], foreground=self.colors["text"], font=("맑은 고딕", 10))
        style.configure("Footer.TLabel", background=self.colors["bg"], foreground=self.colors["muted"], font=("맑은 고딕", 9))
        style.configure("Title.TLabel", background=self.colors["bg"], foreground=self.colors["text"], font=("맑은 고딕", 22, "bold"))
        style.configure("Subtitle.TLabel", background=self.colors["bg"], foreground=self.colors["muted"], font=("맑은 고딕", 12, "bold"))
        style.configure("Brand.TLabel", background=self.colors["bg"], foreground=self.colors["primary"], font=("맑은 고딕", 10, "bold"))
        style.configure("HeaderBody.TLabel", background=self.colors["bg"], foreground=self.colors["muted"], font=("맑은 고딕", 10))
        style.configure("CardTitle.TLabel", background=self.colors["card"], foreground=self.colors["text"], font=("맑은 고딕", 12, "bold"))
        style.configure("Status.TLabel", background=self.colors["card"], foreground=self.colors["text"], font=("맑은 고딕", 16, "bold"))
        style.configure("Success.TLabel", background=self.colors["success_bg"], foreground=self.colors["success"], font=("맑은 고딕", 9, "bold"), padding=(10, 5))
        style.configure("Warning.TLabel", background=self.colors["warning_bg"], foreground=self.colors["warning"], font=("맑은 고딕", 9, "bold"), padding=(10, 5))
        style.configure("Path.TLabel", background=self.colors["soft"], foreground=self.colors["text"], font=("맑은 고딕", 9), padding=(10, 7))

        style.configure("Primary.TButton", background=self.colors["primary"], foreground="#ffffff", borderwidth=0, focusthickness=0, padding=(16, 9), font=("맑은 고딕", 10, "bold"))
        style.map("Primary.TButton", background=[("active", self.colors["primary_active"]), ("disabled", "#a6b5d8")])
        style.configure("Secondary.TButton", background=self.colors["soft"], foreground=self.colors["text"], borderwidth=0, padding=(12, 8), font=("맑은 고딕", 10))
        style.map("Secondary.TButton", background=[("active", "#e2e8f0"), ("disabled", "#eef1f6")])
        style.configure("TCombobox", padding=(8, 5))
        style.configure("Horizontal.TProgressbar", background=self.colors["primary"], troughcolor="#e5e7eb", bordercolor="#e5e7eb", lightcolor=self.colors["primary"], darkcolor=self.colors["primary"])

    def _build_ui(self) -> None:
        self.root.configure(background=self.colors["bg"])
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        outer = ttk.Frame(self.root, style="App.TFrame", padding=(22, 18))
        outer.grid(row=0, column=0, sticky="nsew")
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(1, weight=1)

        self._build_header(outer).grid(row=0, column=0, sticky="ew", pady=(0, 16))

        canvas = tk.Canvas(outer, background=self.colors["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        content = ttk.Frame(canvas, style="App.TFrame")
        content.columnconfigure(0, weight=1)

        content.bind("<Configure>", lambda event: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas_window = canvas.create_window((0, 0), window=content, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind("<Configure>", lambda event: canvas.itemconfigure(canvas_window, width=event.width))

        canvas.grid(row=1, column=0, sticky="nsew")
        scrollbar.grid(row=1, column=1, sticky="ns")

        self._build_key_card(content).grid(row=0, column=0, sticky="ew", pady=(0, 12))
        self._build_transcription_card(content).grid(row=1, column=0, sticky="ew", pady=(0, 12))
        self._build_translation_card(content).grid(row=2, column=0, sticky="ew", pady=(0, 12))
        self._build_progress_card(content).grid(row=3, column=0, sticky="ew", pady=(0, 12))
        self._build_footer(content).grid(row=4, column=0, sticky="ew", pady=(2, 16))

        canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))

    def _build_header(self, parent: ttk.Frame) -> ttk.Frame:
        frame = ttk.Frame(parent, style="App.TFrame")
        frame.columnconfigure(0, weight=1)

        ttk.Label(frame, text=APP_TITLE, style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(frame, text=APP_SUBTITLE, style="Subtitle.TLabel").grid(row=1, column=0, sticky="w", pady=(2, 8))
        ttk.Label(frame, text=APP_BRAND, style="Brand.TLabel").grid(row=2, column=0, sticky="w", pady=(0, 8))
        ttk.Label(frame, text=APP_DESCRIPTION, style="HeaderBody.TLabel").grid(row=3, column=0, sticky="w")
        ttk.Label(
            frame,
            text="영상/오디오는 외부 서버로 업로드되지 않습니다. 번역 기능 사용 시 SRT 텍스트만 Gemini API로 전송됩니다.",
            style="HeaderBody.TLabel",
        ).grid(row=4, column=0, sticky="w", pady=(4, 0))
        return frame

    def _card(self, parent: ttk.Frame, title: str, description: str) -> ttk.Frame:
        frame = ttk.Frame(parent, style="Card.TFrame", padding=(18, 16))
        frame.columnconfigure(0, weight=1)
        ttk.Label(frame, text=title, style="CardTitle.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(frame, text=description, style="Muted.TLabel", wraplength=820).grid(row=1, column=0, sticky="w", pady=(5, 14))
        return frame

    def _file_picker_row(self, parent: ttk.Frame, row: int, label: str, value_var: tk.StringVar, button_text: str, command) -> ttk.Label:
        line = ttk.Frame(parent, style="Card.TFrame")
        line.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        line.columnconfigure(1, weight=1)
        ttk.Label(line, text=label, style="Body.TLabel").grid(row=0, column=0, sticky="w", padx=(0, 12))
        value_label = ttk.Label(line, textvariable=value_var, style="Path.TLabel", anchor="w")
        value_label.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        button = ttk.Button(line, text=button_text, command=command, style="Secondary.TButton")
        button.grid(row=0, column=2, sticky="e")
        return button

    def _build_key_card(self, parent: ttk.Frame) -> ttk.Frame:
        card = self._card(
            parent,
            "Gemini API Key",
            "번역 기능에만 사용됩니다. API Key는 사용자의 PC에 저장되며, 머니체크 서버로 전송되지 않습니다.",
        )
        card.columnconfigure(0, weight=1)

        input_row = ttk.Frame(card, style="Card.TFrame")
        input_row.grid(row=2, column=0, sticky="ew")
        input_row.columnconfigure(0, weight=1)

        self.api_key_entry = ttk.Entry(input_row, show="*", width=48)
        self.api_key_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10), ipady=5)
        self.api_key_entry.insert(0, "")

        self.save_key_button = ttk.Button(input_row, text="저장", command=self._save_api_key, style="Primary.TButton")
        self.save_key_button.grid(row=0, column=1, padx=(0, 6))
        self.delete_key_button = ttk.Button(input_row, text="삭제", command=self._delete_api_key, style="Secondary.TButton")
        self.delete_key_button.grid(row=0, column=2)

        self.key_status_label = ttk.Label(card, textvariable=self.key_status_var, style="Warning.TLabel")
        self.key_status_label.grid(row=3, column=0, sticky="w", pady=(10, 8))
        ttk.Label(
            card,
            text="Gemini API Key는 사용자가 직접 발급해야 합니다. 사용량, 과금, 이용 제한은 Google/Gemini 정책에 따릅니다.",
            style="Muted.TLabel",
            wraplength=820,
        ).grid(row=4, column=0, sticky="w")
        return card

    def _build_transcription_card(self, parent: ttk.Frame) -> ttk.Frame:
        card = self._card(
            parent,
            "SRT/TXT 생성",
            "MP4 또는 MP3 파일에서 음성을 인식해 SRT 자막과 TXT 스크립트를 생성합니다.",
        )

        self.browse_media_button = self._file_picker_row(card, 2, "파일", self.media_display_var, "파일 선택", self._browse_media)
        self.browse_output_button = self._file_picker_row(card, 3, "출력 폴더", self.output_display_var, "폴더 선택", self._browse_output_dir)

        options = ttk.Frame(card, style="Card.TFrame")
        options.grid(row=4, column=0, sticky="ew", pady=(0, 10))
        options.columnconfigure(1, weight=1)
        options.columnconfigure(3, weight=1)

        ttk.Label(options, text="원본 언어", style="Body.TLabel").grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.source_language_combo = ttk.Combobox(
            options,
            textvariable=self.source_language_var,
            values=list(SOURCE_LANGUAGES.keys()),
            state="readonly",
            width=18,
        )
        self.source_language_combo.grid(row=0, column=1, sticky="w", padx=(0, 24))

        ttk.Label(options, text="Whisper 모델", style="Body.TLabel").grid(row=0, column=2, sticky="w", padx=(0, 8))
        self.whisper_model_combo = ttk.Combobox(
            options,
            textvariable=self.whisper_model_var,
            values=WHISPER_MODELS,
            state="readonly",
            width=18,
        )
        self.whisper_model_combo.grid(row=0, column=3, sticky="w")

        ttk.Label(
            card,
            text="small: 빠른 테스트용  |  medium: 기본 추천  |  large-v3: 품질 우선, 느릴 수 있음",
            style="Muted.TLabel",
        ).grid(row=5, column=0, sticky="w", pady=(0, 12))

        self.generate_button = ttk.Button(card, text="자막 생성", command=self._start_transcription, style="Primary.TButton")
        self.generate_button.grid(row=6, column=0, sticky="e")
        return card

    def _build_translation_card(self, parent: ttk.Frame) -> ttk.Frame:
        card = self._card(
            parent,
            "번역 SRT 생성",
            "원본 SRT의 번호와 시간 코드는 유지하고, 자막 텍스트만 번역합니다.",
        )

        self.browse_srt_button = self._file_picker_row(card, 2, "원본 SRT", self.srt_display_var, "SRT 선택", self._browse_srt)

        row = ttk.Frame(card, style="Card.TFrame")
        row.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        row.columnconfigure(1, weight=1)
        ttk.Label(row, text="번역 언어", style="Body.TLabel").grid(row=0, column=0, sticky="w", padx=(0, 12))
        self.target_language_combo = ttk.Combobox(
            row,
            textvariable=self.target_language_var,
            values=list(TARGET_LANGUAGES.keys()),
            state="readonly",
            width=18,
        )
        self.target_language_combo.grid(row=0, column=1, sticky="w")

        ttk.Label(
            card,
            text="번역 기능을 사용할 경우 SRT 자막 텍스트는 Gemini API로 전송됩니다.",
            style="Muted.TLabel",
        ).grid(row=4, column=0, sticky="w", pady=(0, 12))

        self.translate_button = ttk.Button(card, text="번역 SRT 생성", command=self._start_translation, style="Primary.TButton")
        self.translate_button.grid(row=5, column=0, sticky="e")
        return card

    def _build_progress_card(self, parent: ttk.Frame) -> ttk.Frame:
        card = self._card(parent, "진행 상태", "현재 처리 단계, 저장 위치, 사용자 안내 메시지를 확인할 수 있습니다.")
        card.rowconfigure(5, weight=1)

        ttk.Label(card, textvariable=self.stage_var, style="Status.TLabel").grid(row=2, column=0, sticky="w", pady=(0, 8))
        ttk.Progressbar(card, variable=self.progress_var, maximum=100).grid(row=3, column=0, sticky="ew", pady=(0, 12))
        ttk.Label(card, textvariable=self.output_paths_var, style="Path.TLabel", wraplength=820).grid(row=4, column=0, sticky="ew", pady=(0, 10))

        self.log_text = tk.Text(
            card,
            height=8,
            wrap="word",
            state="disabled",
            bg="#fbfcfe",
            fg=self.colors["text"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=self.colors["border"],
            padx=12,
            pady=10,
            font=("맑은 고딕", 9),
        )
        self.log_text.grid(row=5, column=0, sticky="nsew")
        self._log("파일을 선택한 뒤 자막 생성 또는 번역 SRT 생성을 시작하세요.")
        return card

    def _build_footer(self, parent: ttk.Frame) -> ttk.Frame:
        frame = ttk.Frame(parent, style="App.TFrame", padding=(4, 4))
        frame.columnconfigure(0, weight=1)
        lines = [
            "MoReng Subtitle Maker는 머니체크가 만든 로컬 자막 도구입니다.",
            f"GitHub: {GITHUB_URL}",
            f"문의: {CONTACT_EMAIL}",
            "영상/오디오 파일은 외부 서버로 업로드되지 않습니다.",
            "단, 번역 기능을 사용할 경우 SRT의 자막 텍스트는 Gemini API로 전송됩니다.",
            "Gemini API Key는 사용자가 직접 발급하고 직접 입력해야 합니다.",
            "API Key 사용량, 과금, 이용 제한, 번역 결과에 대한 책임은 사용자에게 있습니다.",
        ]
        ttk.Label(frame, text="\n".join(lines), style="Footer.TLabel", justify="left").grid(row=0, column=0, sticky="w")
        return frame

    def _browse_media(self) -> None:
        filetypes = [("Media files", "*.mp4 *.mp3"), ("MP4", "*.mp4"), ("MP3", "*.mp3")]
        path = filedialog.askopenfilename(title="MP4 또는 MP3 파일 선택", filetypes=filetypes)
        if path:
            selected = Path(path)
            self.media_path_var.set(str(selected))
            self.media_display_var.set(selected.name)
            if not self.output_dir_var.get():
                self.output_dir_var.set(str(selected.parent))
                self.output_display_var.set(selected.parent.name or str(selected.parent))
            self._log(f"선택한 미디어 파일: {selected}")

    def _browse_srt(self) -> None:
        path = filedialog.askopenfilename(title="SRT 파일 선택", filetypes=[("SRT files", "*.srt")])
        if path:
            selected = Path(path)
            self.srt_path_var.set(str(selected))
            self.srt_display_var.set(selected.name)
            if not self.output_dir_var.get():
                self.output_dir_var.set(str(selected.parent))
                self.output_display_var.set(selected.parent.name or str(selected.parent))
            self._log(f"선택한 SRT 파일: {selected}")

    def _browse_output_dir(self) -> None:
        path = filedialog.askdirectory(title="출력 폴더 선택")
        if path:
            selected = Path(path)
            self.output_dir_var.set(str(selected))
            self.output_display_var.set(selected.name or str(selected))
            self._log(f"선택한 출력 폴더: {selected}")

    def _save_api_key(self) -> None:
        try:
            saved_to = self.key_store.set_key(self.api_key_entry.get())
        except ValueError as exc:
            messagebox.showwarning("Gemini API Key", str(exc))
            return

        self.api_key_entry.delete(0, tk.END)
        self._refresh_key_status()
        if saved_to == "windows-credential":
            self._log("Gemini API Key가 Windows 자격 증명 저장소에 저장되었습니다.")
        else:
            self._log("Gemini API Key가 로컬 설정 파일에 저장되었습니다.")

    def _delete_api_key(self) -> None:
        self.key_store.delete_key()
        self.api_key_entry.delete(0, tk.END)
        self._refresh_key_status()
        self._log("Gemini API Key가 삭제되었습니다.")

    def _refresh_key_status(self) -> None:
        if self.key_store.has_key():
            self.key_status_var.set("저장됨 (********)")
            self.key_status_label.configure(style="Success.TLabel")
        else:
            self.key_status_var.set("저장 안 됨")
            self.key_status_label.configure(style="Warning.TLabel")

    def _start_transcription(self) -> None:
        if self.is_busy:
            return

        media_path = Path(self.media_path_var.get().strip())
        if not media_path.exists():
            messagebox.showwarning("파일 선택", "MP4 또는 MP3 파일을 먼저 선택해주세요.")
            return
        if media_path.suffix.lower() not in SUPPORTED_MEDIA_EXTENSIONS:
            messagebox.showwarning("파일 형식", "현재 버전은 .mp4, .mp3 파일만 지원합니다.")
            return

        output_dir = Path(self.output_dir_var.get().strip() or media_path.parent)
        source_language = SOURCE_LANGUAGES[self.source_language_var.get()]
        model_size = self.whisper_model_var.get()

        self._set_busy(True)
        self._set_status("자막 생성 준비 중", 0)
        thread = threading.Thread(
            target=self._transcription_worker,
            args=(media_path, output_dir, source_language, model_size),
            daemon=True,
        )
        thread.start()

    def _transcription_worker(
        self,
        media_path: Path,
        output_dir: Path,
        source_language: str | None,
        model_size: str,
    ) -> None:
        try:
            self._emit("progress", ("오디오 길이 확인 중", 2.0))
            self._emit("log", f"처리 파일: {media_path}")
            duration = get_duration_seconds(media_path)

            with tempfile.TemporaryDirectory(prefix="moreng_subtitle_") as temp_dir:
                self._emit("progress", ("오디오 추출 중", 8.0))
                audio_path = extract_audio_to_wav(media_path, temp_dir)

                self._emit("progress", (f"Whisper {model_size} 모델 준비 중", 12.0))
                engine = WhisperEngine(model_size=model_size)

                def stt_progress(stage: str, ratio: float) -> None:
                    self._emit("progress", (stage, 12.0 + ratio * 76.0))

                result = engine.transcribe(
                    audio_path,
                    language_code=source_language,
                    duration_seconds=duration,
                    progress_callback=stt_progress,
                )

            language_code = normalize_language_code(result.detected_language or source_language)
            srt_path, txt_path = subtitle_output_paths(media_path, output_dir, language_code)

            self._emit("progress", ("SRT 저장 중", 92.0))
            write_srt(result.segments, srt_path)

            self._emit("progress", ("TXT 저장 중", 96.0))
            write_transcript(result.segments, txt_path)

            detected = language_code or "원본"
            self._emit("last_srt", str(srt_path))
            self._emit("paths", f"SRT: {srt_path}\nTXT: {txt_path}")
            self._emit("done", f"{detected} SRT/TXT 생성 완료")
            self._emit("log", f"SRT 저장: {srt_path}")
            self._emit("log", f"TXT 저장: {txt_path}")
        except Exception as exc:
            self._emit("error", self._friendly_error("자막 생성", exc))
        finally:
            self._emit("busy", False)

    def _start_translation(self) -> None:
        if self.is_busy:
            return

        selected_srt = self.srt_path_var.get().strip()
        if not selected_srt and self.last_srt_path:
            selected_srt = str(self.last_srt_path)
            self.srt_path_var.set(selected_srt)
            self.srt_display_var.set(self.last_srt_path.name)

        srt_path = Path(selected_srt)
        if not srt_path.exists():
            messagebox.showwarning("SRT 선택", "번역할 원본 SRT 파일을 선택해주세요.")
            return

        api_key = self.key_store.get_key()
        if not api_key:
            messagebox.showwarning("Gemini API Key", "Gemini API Key가 저장되어 있지 않습니다.")
            return

        output_dir = Path(self.output_dir_var.get().strip() or srt_path.parent)
        target_label = self.target_language_var.get()
        target_code, target_name = TARGET_LANGUAGES[target_label]

        self._set_busy(True)
        self._set_status(f"{target_label} 번역 SRT 생성 준비 중", 0)
        thread = threading.Thread(
            target=self._translation_worker,
            args=(srt_path, output_dir, target_code, target_name, target_label, api_key),
            daemon=True,
        )
        thread.start()

    def _translation_worker(
        self,
        srt_path: Path,
        output_dir: Path,
        target_code: str,
        target_name: str,
        target_label: str,
        api_key: str,
    ) -> None:
        try:
            self._emit("progress", ("SRT 읽는 중", 5.0))
            blocks = read_srt(srt_path)
            output_srt_path = translated_srt_output_path(srt_path, output_dir, target_code)

            self._emit("progress", (f"{target_label} 번역 SRT 생성 중", 10.0))
            translator = GeminiTranslator(api_key=api_key)

            def translation_progress(stage: str, ratio: float) -> None:
                self._emit("progress", (f"{target_label} {stage}", 10.0 + ratio * 82.0))

            translated_blocks, failures = translator.translate_blocks(
                blocks,
                target_language_name=target_name,
                progress_callback=translation_progress,
            )

            self._emit("progress", ("번역 SRT 저장 중", 96.0))
            save_srt_blocks(translated_blocks, output_srt_path)
            failure_log = write_failure_log(failures, output_srt_path)

            self._emit("paths", f"번역 SRT: {output_srt_path}")
            self._emit("done", f"{target_label} 번역 SRT 생성 완료")
            self._emit("log", f"번역 SRT 저장: {output_srt_path}")
            if failure_log:
                self._emit("log", f"일부 블록은 원문으로 유지되었습니다. 로그: {failure_log}")
        except Exception as exc:
            self._emit("error", self._friendly_error("번역", exc))
        finally:
            self._emit("busy", False)

    def _friendly_error(self, action: str, exc: Exception) -> str:
        raw = str(exc)
        raw_lower = raw.lower()
        if "ffmpeg" in raw_lower or "ffprobe" in raw_lower:
            return "ffmpeg를 찾을 수 없습니다. 설치전_필독.txt 또는 README의 ffmpeg 설치 안내를 확인해주세요."
        if "SRT" in raw or "srt" in raw:
            return "선택한 SRT 파일을 읽을 수 없습니다. 파일 형식과 내용을 확인해주세요."
        if "503" in raw or "UNAVAILABLE" in raw or "high demand" in raw_lower:
            return "Gemini 모델이 일시적으로 혼잡합니다. 잠시 후 다시 시도해주세요."
        if "429" in raw or "RESOURCE_EXHAUSTED" in raw or "rate limit" in raw_lower:
            return "Gemini 사용량 제한 또는 요청 제한에 걸렸습니다. 잠시 후 다시 시도하거나 Google/Gemini 사용량을 확인해주세요."
        if "API Key" in raw or "api key" in raw_lower or "Gemini" in raw:
            return "Gemini API Key 또는 Gemini 번역 요청을 확인해주세요. API Key 저장 상태와 사용량 제한을 확인할 수 있습니다."
        return f"{action} 중 오류가 발생했습니다: {raw}"

    def _set_busy(self, busy: bool) -> None:
        self.is_busy = busy
        state = "disabled" if busy else "normal"
        for button in [
            self.save_key_button,
            self.delete_key_button,
            self.browse_media_button,
            self.browse_output_button,
            self.browse_srt_button,
            self.generate_button,
            self.translate_button,
        ]:
            button.configure(state=state)

    def _set_status(self, stage: str, value: float) -> None:
        self.stage_var.set(stage)
        self.progress_var.set(value)

    def _emit(self, event_type: str, payload: object) -> None:
        self.events.put((event_type, payload))

    def _poll_events(self) -> None:
        try:
            while True:
                event_type, payload = self.events.get_nowait()
                if event_type == "progress":
                    stage, value = payload  # type: ignore[misc]
                    self._set_status(str(stage), float(value))
                elif event_type == "log":
                    self._log(str(payload))
                elif event_type == "paths":
                    self.output_paths_var.set(str(payload))
                elif event_type == "last_srt":
                    self.last_srt_path = Path(str(payload))
                    self.srt_path_var.set(str(payload))
                    self.srt_display_var.set(Path(str(payload)).name)
                elif event_type == "done":
                    self.progress_var.set(100.0)
                    self.stage_var.set(str(payload))
                    self._log(str(payload))
                elif event_type == "error":
                    self.stage_var.set("오류 발생")
                    self._log(str(payload))
                    messagebox.showerror("오류", str(payload))
                elif event_type == "busy":
                    self._set_busy(bool(payload))
        except queue.Empty:
            pass
        self.root.after(100, self._poll_events)

    def _log(self, message: str) -> None:
        self.log_text.configure(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state="disabled")


def main() -> None:
    root = tk.Tk()
    SubtitleToolApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
