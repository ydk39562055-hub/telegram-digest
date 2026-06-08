"""비대화식 로그인 헬퍼 (2단계).

  1) python login_helper.py send "+82..."     → 인증코드를 텔레그램에 발송
  2) python login_helper.py code 12345         → 받은 코드로 로그인 완료
     (2단계 비밀번호가 있으면)  python login_helper.py code 12345 비밀번호

전화번호/코드 사이 상태(phone_code_hash)는 .login_state.json 에 잠깐 저장된다.
"""
import asyncio
import json
import sys

from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

import config

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

STATE = config.BASE_DIR / ".login_state.json"


async def send(phone: str):
    client = TelegramClient(config.TG_SESSION, config.TG_API_ID, config.TG_API_HASH)
    await client.connect()
    if await client.is_user_authorized():
        me = await client.get_me()
        print(f"이미 로그인돼 있음: {me.first_name} (@{me.username}) — 추가 작업 불필요")
        await client.disconnect()
        return
    sent = await client.send_code_request(phone)
    STATE.write_text(
        json.dumps({"phone": phone, "hash": sent.phone_code_hash}, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"📨 인증코드를 텔레그램 앱({phone})으로 보냈다. 앱에서 코드 확인 후 알려달라.")
    await client.disconnect()


async def code(the_code: str, password: str | None):
    if not STATE.exists():
        print("⚠ 먼저 'send' 단계를 실행해야 한다.")
        return
    st = json.loads(STATE.read_text(encoding="utf-8"))
    client = TelegramClient(config.TG_SESSION, config.TG_API_ID, config.TG_API_HASH)
    await client.connect()
    try:
        await client.sign_in(st["phone"], the_code, phone_code_hash=st["hash"])
    except SessionPasswordNeededError:
        if not password:
            print("🔐 2단계 비밀번호가 필요하다. `python login_helper.py code <코드> <비밀번호>` 로 다시.")
            await client.disconnect()
            return
        await client.sign_in(password=password)

    me = await client.get_me()
    print(f"✅ 로그인 완료: {me.first_name} (@{me.username})")
    print(f"   세션: {config.TG_SESSION}.session")
    try:
        STATE.unlink()  # 임시 상태 삭제
    except Exception:
        pass
    await client.disconnect()


async def main():
    if len(sys.argv) < 3:
        print('사용법: python login_helper.py send "+82..."  또는  python login_helper.py code 12345')
        return
    cmd = sys.argv[1]
    if cmd == "send":
        await send(sys.argv[2])
    elif cmd == "code":
        pw = sys.argv[3] if len(sys.argv) > 3 else None
        await code(sys.argv[2], pw)
    else:
        print("알 수 없는 명령:", cmd)


if __name__ == "__main__":
    asyncio.run(main())
