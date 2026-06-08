"""로컬 파일 세션 → 문자열 세션(StringSession)으로 변환해 출력.

클라우드(깃허브 액션)에서 로그인 없이 쓰려면 이 문자열을 GitHub Secret
(TG_SESSION_STRING) 으로 등록한다.

  python export_session.py            # 화면에 출력(민감)
  python export_session.py --file     # session_string.txt 로 저장(화면 노출 X)
"""
import asyncio
import sys

from telethon import TelegramClient
from telethon.sessions import StringSession

import config


async def main():
    client = TelegramClient(config.TG_SESSION, config.TG_API_ID, config.TG_API_HASH)
    await client.connect()
    if not await client.is_user_authorized():
        print("⚠ 로그인 안 됨. login_helper 로 먼저 로그인.")
        await client.disconnect()
        return
    s = StringSession.save(client.session)
    if "--file" in sys.argv:
        out = config.BASE_DIR / "session_string.txt"
        out.write_text(s, encoding="utf-8")
        print(f"저장됨: {out} (등록 후 삭제 권장)")
    else:
        print(s)
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
