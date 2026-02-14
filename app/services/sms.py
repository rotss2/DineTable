from __future__ import annotations
import re
import requests
from typing import Optional

def normalize_phone(raw: str) -> str:
    s = (raw or "").strip()
    if not s:
        return ""
    s = re.sub(r"[^\d+]", "", s)
    if s.startswith("09") and len(s) == 11:
        return "+63" + s[1:]
    if s.startswith("9") and len(s) == 10:
        return "+63" + s
    if s.startswith("63") and len(s) == 12:
        return "+" + s
    if s.startswith("+63") and len(s) == 13:
        return s
    digits = re.sub(r"\D", "", s)
    if digits.startswith("63") and len(digits) >= 12:
        return "+" + digits
    return s

def send_semaphore_sms(api_key: str, sender: str, to_phone: str, message: str) -> tuple[bool, str]:
    if not api_key:
        return False, "SEMAPHORE_API_KEY not set"
    to = normalize_phone(to_phone)
    if not to:
        return False, "Empty/invalid phone"

    try:
        resp = requests.post(
            "https://semaphore.co/api/v4/messages",
            data={"apikey": api_key, "number": to, "message": message, "sendername": sender},
            timeout=15,
        )
        ok = resp.ok
        return ok, f"HTTP {resp.status_code}: {resp.text[:200]}"
    except Exception as e:
        return False, f"Exception: {e!r}"
