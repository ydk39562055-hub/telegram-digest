"""최초 1회만 실행: 텔레그램 로그인 → .session 파일 생성.

실행하면 전화번호와 인증코드를 물어본다. 한 번 로그인하면
digest.session 파일이 생기고, 이후 fetch는 자동 로그인된다.
"""
import asyncio
import sys

from telethon import TelegramClient

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import config


async def main():
    if not config.TG_API_ID or not config.TG_API_HASH:
        print("⚠ .env 의 TG_API_ID / TG_API_HASH 를 먼저 채워라.")
        return
    client = TelegramClient(config.TG_SESSION, config.TG_API_ID, config.TG_API_HASH)
    await client.start()  # 전화번호+코드 입력 유도
    me = await client.get_me()
    print(f"✅ 로그인 완료: {me.first_name} (@{me.username})")
    print(f"   세션 파일: {config.TG_SESSION}.session  (이제 main.py 가 자동 로그인됨)")
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
