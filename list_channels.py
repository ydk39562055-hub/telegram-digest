"""내가 구독/참여 중인 텔레그램 채널·그룹 목록과 아이디를 보여준다.

login.py 로 로그인(.session 생성)한 뒤 실행:
    python list_channels.py

출력: 이름 / @username / 숫자ID
@username 이 있는 채널은 그대로 .env 의 CHANNELS 에 넣으면 되고,
username 이 없는(비공개) 채널은 숫자ID(-100...)를 넣으면 된다.
"""
import asyncio
import sys

from telethon import TelegramClient

import config

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


async def main():
    if not config.TG_API_ID or not config.TG_API_HASH:
        print("⚠ .env 의 TG_API_ID / TG_API_HASH 를 먼저 채워라.")
        return

    client = TelegramClient(config.TG_SESSION, config.TG_API_ID, config.TG_API_HASH)
    await client.connect()
    if not await client.is_user_authorized():
        print("⚠ 로그인 안 됨. 먼저 `python login.py` 를 실행하라.")
        await client.disconnect()
        return

    rows = []
    async for dialog in client.iter_dialogs():
        # 채널/그룹만 (1:1 개인 대화 제외)
        if not (dialog.is_channel or dialog.is_group):
            continue
        ent = dialog.entity
        username = getattr(ent, "username", None)
        rows.append(
            {
                "name": dialog.name or "(이름없음)",
                "username": f"@{username}" if username else "(없음)",
                "id": dialog.id,
                "broadcast": getattr(ent, "broadcast", False),  # True=채널, False=그룹
            }
        )

    # 채널(broadcast) 먼저, 그 다음 그룹
    rows.sort(key=lambda r: (not r["broadcast"], r["name"]))

    print(f"\n=== 구독/참여 중인 채널·그룹 {len(rows)}개 ===\n")
    print(f"{'종류':<5} {'이름':<28} {'username':<22} {'숫자ID'}")
    print("-" * 80)
    for r in rows:
        kind = "채널" if r["broadcast"] else "그룹"
        name = (r["name"][:26] + "…") if len(r["name"]) > 27 else r["name"]
        print(f"{kind:<5} {name:<28} {r['username']:<22} {r['id']}")

    # .env 에 바로 붙여넣기 좋은 줄도 만들어줌 (username 있는 것만)
    usable = [r["username"] for r in rows if r["username"] != "(없음)"]
    if usable:
        print("\n--- .env 의 CHANNELS 에 붙여넣기 좋은 형태(username 있는 것만) ---")
        print("CHANNELS=" + ",".join(usable))

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
