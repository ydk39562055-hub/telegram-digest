"""Telethon으로 채널들의 최근 N시간 메시지(텍스트 + 이미지)를 가져온다.

사용자 점검 체크리스트를 코드에 그대로 박아 화면에 출력한다:
  1) CHANNELS 리스트가 채워져 있나
  2) Telethon 로그인(세션)이 됐나
  3) fetch가 채널별로 메시지를 몇 개 반환하나  (print(len(messages)))
"""
from datetime import datetime, timedelta, timezone

from telethon.tl.functions.messages import GetDialogFiltersRequest

import config
from tgclient import make_client


async def _resolve_targets(client):
    """다이제스트 대상 목록을 정한다.
    FOLDER 가 지정돼 있으면 그 텔레그램 채팅 폴더의 채널들을 쓰고(자동 동기화),
    아니면 .env 의 CHANNELS 목록을 쓴다.
    반환: [(표시이름, 대상)]  대상은 iter_messages 에 넣을 entity/username.
    """
    if config.FOLDER:
        res = await client(GetDialogFiltersRequest())
        filters = getattr(res, "filters", res)
        wanted = config.FOLDER.strip()
        # 진단: 이 계정에 있는 모든 폴더와 포함 채널 수
        for f in filters:
            t = getattr(f, "title", None); tt = getattr(t, "text", t)
            if tt is None: continue
            print(f"[진단] 폴더 '{str(tt).strip()}' → 포함 {len(getattr(f, 'include_peers', []) or [])}개")
        for f in filters:
            title = getattr(f, "title", None)
            if title is None:
                continue
            title_text = getattr(title, "text", title)
            if str(title_text).strip() != wanted:
                continue
            targets = []
            for peer in (getattr(f, "include_peers", []) or []):
                try:
                    ent = await client.get_entity(peer)
                except Exception:
                    continue
                # 채널/그룹만 (개인 대화 제외)
                if not (getattr(ent, "broadcast", False) or getattr(ent, "megagroup", False)):
                    continue
                name = getattr(ent, "title", None) or getattr(ent, "username", "?")
                targets.append((name, ent))
            print(f"[점검1] FOLDER='{wanted}' → 채널 {len(targets)}개")
            return targets
        print(f"[점검1] ⚠ '{wanted}' 폴더를 못 찾음. (list_folders.py 로 폴더명 확인) 빈 결과.")
        return []

    print(f"[점검1] CHANNELS = {config.CHANNELS}")
    if not config.CHANNELS:
        print("[점검1] ⚠ CHANNELS 도 FOLDER 도 비어 있음 → .env 확인. 빈 결과.")
        return []
    return [(ch, ch) for ch in config.CHANNELS]


async def fetch_all():
    """반환: { 채널명: [ {time, text, images:[bytes]} , ... ] }"""

    if not config.TG_API_ID or not config.TG_API_HASH:
        print("[점검2] ⚠ TG_API_ID / TG_API_HASH 가 비어 있음 → .env 확인 필요. 빈 결과 반환.")
        return {}

    if config.SINCE_MIDNIGHT:
        # 한국시간 기준 오늘 0시 → UTC 로 변환해 비교
        now_kst = datetime.now(config.TZ)
        midnight_kst = now_kst.replace(hour=0, minute=0, second=0, microsecond=0)
        cutoff = midnight_kst.astimezone(timezone.utc)
        print(f"[수집범위] 오늘 0시(한국)부터 — {midnight_kst:%Y-%m-%d %H:%M} ~ 지금")
    else:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=config.HOURS)
        print(f"[수집범위] 최근 {config.HOURS}시간")
    result: dict[str, list] = {}

    client = make_client()
    await client.connect()

    # --- 점검 2: 세션 로그인 여부 ---
    authorized = await client.is_user_authorized()
    print(f"[점검2] Telethon 세션 로그인됨? {authorized}")
    if not authorized:
        print(
            "[점검2] ⚠ 로그인 안 됨. 먼저 `python login_helper.py` 로 로그인하면 "
            ".session 파일이 생긴다. 빈 결과 반환."
        )
        await client.disconnect()
        return {}

    # 진단: 봇이 로그인된 계정 (전화번호는 공개 로그라 제외)
    try:
        me = await client.get_me()
        print(f"[점검2.5] 로그인 계정: {getattr(me, 'first_name', '') or ''} / @{getattr(me, 'username', None)} / id={getattr(me, 'id', None)}")
    except Exception as e:
        print(f"[점검2.5] 계정 조회 실패: {e}")

    # --- 점검 1: 대상 채널 확정 (폴더 또는 CHANNELS) ---
    targets = await _resolve_targets(client)
    if not targets:
        await client.disconnect()
        return {}

    for name, ch in targets:
        messages = []
        img_budget = config.MAX_IMAGES_PER_CHANNEL  # 채널당 이미지 예산
        try:
            async for msg in client.iter_messages(ch):
                if msg.date < cutoff:
                    break  # 최신순이라, 24시간보다 오래되면 그만
                if not (msg.text or msg.photo):
                    continue

                images = []
                if msg.photo and img_budget > 0:
                    data = await client.download_media(msg, file=bytes)
                    if data:
                        images.append(data)
                        img_budget -= 1

                messages.append(
                    {
                        # 텔레그램 시간은 UTC → 한국시간으로 변환해 표시
                        "time": msg.date.astimezone(config.TZ).strftime("%H:%M"),
                        "text": msg.text or "",
                        "images": images,
                    }
                )
        except Exception as e:  # 채널 접근 실패 등은 건너뛰되 알림
            print(f"[fetch] ⚠ '{name}' 가져오기 실패: {e}")

        messages.reverse()  # 오래된→최신 (읽기 순서)
        result[str(name)] = messages
        # --- 점검 3: 채널별 메시지 개수 ---
        n_img = sum(len(m["images"]) for m in messages)
        print(f"[점검3] {name}: 메시지 {len(messages)}개, 이미지 {n_img}장")

    await client.disconnect()

    total = sum(len(v) for v in result.values())
    print(f"[점검3] 합계: 메시지 {total}개")
    return result
