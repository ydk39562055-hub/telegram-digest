"""최종 다이제스트를 비공개 채널로 전송.

- BOT_TOKEN 이 있으면 '봇'으로 발송 → 내 알림이 울린다(본인 계정이 올리면 알림 안 옴).
  없으면 기존처럼 사용자 계정(TG_SESSION)으로 발송.
- 글은 Gemini가 넣은 `@@@` 구분자 기준으로 블록을 나눠 '주제 블록당 메시지 1개'로 보낸다.
  (폰에서 한 덩어리로 길게 오지 않고, 주제별로 짧게 나뉘어 읽기 좋게.)
- 블록 하나가 텔레그램 한 메시지 한도(4096자)를 넘으면 그 블록만 줄 단위로 더 쪼갠다.
"""
import json
import urllib.error
import urllib.request

import config


def _split_blocks(text: str, size: int = 3900):
    """`@@@` 로 주제 블록 분리. 너무 긴 블록은 줄 단위로 추가 분할."""
    blocks = [b.strip() for b in text.split("@@@")]
    blocks = [b for b in blocks if b]
    if not blocks:
        blocks = [text.strip()]

    out = []
    for block in blocks:
        if len(block) <= size:
            out.append(block)
            continue
        cur = ""
        for line in block.split("\n"):
            if len(cur) + len(line) + 1 > size:
                if cur:
                    out.append(cur)
                while len(line) > size:
                    out.append(line[:size])
                    line = line[size:]
                cur = line
            else:
                cur = (cur + "\n" + line) if cur else line
        if cur:
            out.append(cur)
    return out


def _send_via_bot(parts):
    url = f"https://api.telegram.org/bot{config.BOT_TOKEN}/sendMessage"
    for chunk in parts:
        body = json.dumps({
            "chat_id": int(config.DEST_CHANNEL),
            "text": chunk,
            "disable_web_page_preview": True,
        }).encode("utf-8")
        req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                r.read()
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "ignore")[:300]
            print(f"[전송] ⚠ 봇 발송 실패 {e.code}: {detail}")
            raise
    print(f"[전송] ✅ 봇으로 전송 완료 ({len(parts)}개 메시지)")


async def _send_via_user(parts):
    from tgclient import make_client

    client = make_client()
    await client.connect()
    if not await client.is_user_authorized():
        print("[전송] ⚠ 로그인 안 됨 → 전송 생략")
        await client.disconnect()
        return
    dest = int(config.DEST_CHANNEL)
    for chunk in parts:
        await client.send_message(dest, chunk, link_preview=False)
    print(f"[전송] ✅ 사용자 계정으로 전송 완료 ({len(parts)}개 메시지)")
    await client.disconnect()


async def send_digest(text: str):
    if not config.DEST_CHANNEL:
        print("[전송] DEST_CHANNEL 비어 있음 → 전송 생략")
        return
    parts = _split_blocks(text)
    if config.BOT_TOKEN:
        _send_via_bot(parts)
    else:
        await _send_via_user(parts)
