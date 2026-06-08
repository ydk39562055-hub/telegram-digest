"""다이제스트를 받을 비공개 채널을 1회 생성하고, 그 채널 id를 출력한다.

  python create_dest_channel.py

출력된 DEST_CHANNEL 값을 .env 에 넣으면 된다.
이미 같은 이름의 채널이 있어도 중복 생성하지 않도록 먼저 확인한다.
"""
import asyncio
import sys

from telethon import utils
from telethon.tl.functions.channels import CreateChannelRequest

import config
from tgclient import make_client

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

TITLE = "📊 투자 다이제스트"
ABOUT = "텔레그램 메크로 분석 폴더 24시간 요약 (자동)"


async def main():
    client = make_client()
    await client.connect()
    if not await client.is_user_authorized():
        print("⚠ 로그인 안 됨. login_helper 로 먼저 로그인.")
        await client.disconnect()
        return

    # 이미 있으면 재사용
    async for dialog in client.iter_dialogs():
        if dialog.name == TITLE:
            print(f"이미 존재함 → DEST_CHANNEL={utils.get_peer_id(dialog.entity)}")
            await client.disconnect()
            return

    res = await client(CreateChannelRequest(title=TITLE, about=ABOUT, megagroup=False))
    chat = res.chats[0]
    dest = utils.get_peer_id(chat)
    print(f"✅ 비공개 채널 생성됨: {TITLE}")
    print(f"DEST_CHANNEL={dest}")
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
