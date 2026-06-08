"""최종 다이제스트를 비공개 채널(DEST_CHANNEL)로 전송. 4096자 제한 → 나눠 보냄."""
import config
from tgclient import make_client


def _chunks(text: str, size: int = 3900):
    """줄 단위로 자르되 한 덩어리가 size 를 넘지 않게."""
    out, cur = [], ""
    for line in text.split("\n"):
        if len(cur) + len(line) + 1 > size:
            if cur:
                out.append(cur)
            # 한 줄이 통째로 너무 길면 강제로 쪼갬
            while len(line) > size:
                out.append(line[:size])
                line = line[size:]
            cur = line
        else:
            cur = (cur + "\n" + line) if cur else line
    if cur:
        out.append(cur)
    return out


async def send_digest(text: str):
    if not config.DEST_CHANNEL:
        print("[전송] DEST_CHANNEL 비어 있음 → 전송 생략")
        return
    client = make_client()
    await client.connect()
    if not await client.is_user_authorized():
        print("[전송] ⚠ 로그인 안 됨 → 전송 생략")
        await client.disconnect()
        return

    dest = int(config.DEST_CHANNEL)
    parts = _chunks(text)
    for i, chunk in enumerate(parts, 1):
        header = f"({i}/{len(parts)})\n" if len(parts) > 1 else ""
        await client.send_message(dest, header + chunk, link_preview=False)
    print(f"[전송] ✅ 비공개 채널로 전송 완료 ({len(parts)}개 메시지)")
    await client.disconnect()
