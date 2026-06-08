"""'.env' 형식 점검: 각 값이 채워졌는지, 자리표시자([..])인지, 형식이 맞는지 확인."""
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import config


def is_placeholder(v: str) -> bool:
    return (not v) or ("[" in str(v) and "]" in str(v)) or "채널1" in str(v)


print("=== .env 형식 점검 ===")
ok = True

# TG_API_ID: 0이 아니고 숫자여야 함
if config.TG_API_ID and config.TG_API_ID > 0:
    print(f"✅ TG_API_ID      : 숫자 OK ({config.TG_API_ID})")
else:
    print("❌ TG_API_ID      : 비었거나 숫자가 아님 → my.telegram.org 의 api_id 숫자 입력")
    ok = False

for name, val in [
    ("TG_API_HASH", config.TG_API_HASH),
    ("GEMINI_API_KEY", config.GEMINI_API_KEY),
]:
    if is_placeholder(val):
        print(f"❌ {name:<14}: 아직 자리표시자/빈값 → 실제 키 입력 필요")
        ok = False
    else:
        masked = val[:4] + "…" + val[-3:] if len(val) > 8 else "(짧음)"
        print(f"✅ {name:<14}: 채워짐 ({masked})")

# CHANNELS
if not config.CHANNELS or any(is_placeholder(c) for c in config.CHANNELS):
    print(f"❌ CHANNELS       : 자리표시자/빈값 {config.CHANNELS} → 실제 @채널명 입력")
    ok = False
else:
    print(f"✅ CHANNELS       : {len(config.CHANNELS)}개 {config.CHANNELS}")

print(f"✅ GEMINI_MODEL   : {config.GEMINI_MODEL}")
print(f"✅ HOURS          : {config.HOURS}")
print(f"✅ MAX_IMAGES     : {config.MAX_IMAGES_PER_CHANNEL}")

print("\n" + ("🎉 형식 OK — 실제 값까지 다 채워짐. login.py → main.py 진행 가능."
              if ok else
              "⚠ 위 ❌ 항목에 '실제 값'을 넣어야 동작함. (지금은 자리표시자 상태)"))
