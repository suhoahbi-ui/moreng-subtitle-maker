from __future__ import annotations

import base64
import json
import os
from pathlib import Path


SERVICE_NAME = "moreng-subtitle-maker"
LEGACY_SERVICE_NAME = "local-subtitle-tool"
ACCOUNT_NAME = "gemini-api-key"


class KeyStore:
    def __init__(self) -> None:
        self._keyring = None
        try:
            import keyring

            self._keyring = keyring
        except ImportError:
            self._keyring = None

    @property
    def fallback_file(self) -> Path:
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / ".local-subtitle-tool"))
        return base / "MoRengSubtitleMaker" / "secrets.json"

    @property
    def legacy_fallback_file(self) -> Path:
        # Keep this so users upgrading from the pre-MoReng prototype can still delete old keys.
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / ".local-subtitle-tool"))
        return base / "LocalSubtitleTool" / "secrets.json"

    def get_key(self) -> str | None:
        if self._keyring is not None:
            for service_name in [SERVICE_NAME, LEGACY_SERVICE_NAME]:
                try:
                    value = self._keyring.get_password(service_name, ACCOUNT_NAME)
                    if value:
                        return value
                except Exception:
                    pass
        return self._read_fallback_key()

    def has_key(self) -> bool:
        return bool(self.get_key())

    def set_key(self, api_key: str) -> str:
        value = api_key.strip()
        if not value:
            raise ValueError("API Key가 비어 있습니다.")

        if self._keyring is not None:
            try:
                self._keyring.set_password(SERVICE_NAME, ACCOUNT_NAME, value)
                self._delete_fallback_key()
                return "windows-credential"
            except Exception:
                pass

        self._write_fallback_key(value)
        return "local-file"

    def delete_key(self) -> None:
        if self._keyring is not None:
            try:
                self._keyring.delete_password(SERVICE_NAME, ACCOUNT_NAME)
            except Exception:
                pass
            try:
                self._keyring.delete_password(LEGACY_SERVICE_NAME, ACCOUNT_NAME)
            except Exception:
                pass
        self._delete_fallback_key()

    def _read_fallback_key(self) -> str | None:
        path = self.fallback_file if self.fallback_file.exists() else self.legacy_fallback_file
        if not path.exists():
            return None
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            encoded = payload.get("gemini_api_key", "")
            if not encoded:
                return None
            return base64.b64decode(encoded.encode("ascii")).decode("utf-8")
        except Exception:
            return None

    def _write_fallback_key(self, api_key: str) -> None:
        path = self.fallback_file
        path.parent.mkdir(parents=True, exist_ok=True)
        encoded = base64.b64encode(api_key.encode("utf-8")).decode("ascii")
        path.write_text(json.dumps({"gemini_api_key": encoded}, indent=2), encoding="utf-8")

    def _delete_fallback_key(self) -> None:
        try:
            self.fallback_file.unlink(missing_ok=True)
        except Exception:
            pass
        try:
            self.legacy_fallback_file.unlink(missing_ok=True)
        except Exception:
            pass
