"""내 텔레그램 채팅 폴더(폴더별 채널 묶음)를 보여준다.

  python list_folders.py
"""
import asyncio
import sys

from telethon import TelegramClient
from telethon.tl.functions.messages import GetDialogFiltersRequest

import config

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


async def main():
    client = TelegramClient(config.TG_SESSION, config.TG_API_ID, config.TG_API_HASH)
    await client.connect()
    if not await client.is_user_authorized():
        print("⚠ 로그인 안 됨. login_helper 로 먼저 로그인.")
        await client.disconnect()
        return

    res = await client(GetDialogFiltersRequest())
    filters = getattr(res, "filters", res)

    for f in filters:
        title = getattr(f, "title", None)
        if title is None:
            continue  # 기본('모든 채팅') 등은 건너뜀
        # title 이 TextWithEntities 객체일 수 있음
        title_text = getattr(title, "text", title)
        include = getattr(f, "include_peers", []) or []
        print(f"\n📁 폴더: {title_text}  (포함 {len(include)}개)")
        for peer in include:
            try:
                ent = await client.get_entity(peer)
            except Exception:
                continue
            uname = getattr(ent, "username", None)
            name = getattr(ent, "title", getattr(ent, "first_name", "?"))
            print(f"   - {name}  {'@'+uname if uname else '(username없음)'}")

        usable = []
        for peer in include:
            try:
                ent = await client.get_entity(peer)
            except Exception:
                continue
            if getattr(ent, "username", None):
                usable.append("@" + ent.username)
        if usable:
            print("   CHANNELS=" + ",".join(usable))

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
