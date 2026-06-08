"""전체 파이프라인.

흐름:
  1) fetch_all()  — 채널들의 최근 24시간 글(텍스트+이미지)
  2) 채널별 1차 요약 (Gemini, 이미지 포함)
  3) 1차 요약 합치기 → 최종 다이제스트 (Gemini)
  4) 화면 출력 + 날짜별 .md 파일 저장

가드: 가져온 메시지가 0개면 사람에게 아무것도 요청하지 않고
      '오늘은 새 메시지 없음' 만 출력하고 종료한다.
"""
import asyncio
import sys
import time
from datetime import datetime
from pathlib import Path

# Windows 한글 콘솔(cp949)에서 이모지/한글 출력이 깨지거나 죽지 않게 UTF-8 고정
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

import config
import deliver
import digest
from fetch import fetch_all

OUT_DIR = Path(__file__).parent / "출력"


def _wait_until_send_time():
    """SEND_AT('HH:MM', 한국시간)이 지정되면 그 시각 정각까지 대기.
    이미 지났으면 즉시 발송."""
    if not config.SEND_AT:
        return
    try:
        hh, mm = (int(x) for x in config.SEND_AT.split(":"))
    except ValueError:
        print(f"[전송] SEND_AT 형식 오류('{config.SEND_AT}') → 즉시 발송")
        return
    now = datetime.now(config.TZ)
    target = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
    wait = (target - now).total_seconds()
    if wait > 0:
        print(f"[전송] {config.SEND_AT}(한국) 정각 발송까지 {int(wait)}초 대기…")
        time.sleep(wait)
    else:
        print(f"[전송] 이미 {config.SEND_AT} 지남 → 즉시 발송")


async def run():
    data = await fetch_all()  # { 채널: [메시지...] }

    total = sum(len(v) for v in data.values())
    if total == 0:
        # === 폴백 차단 가드 ===
        print("\n오늘은 새 메시지 없음")
        return

    # 2) 채널별 1차 요약 (무료 등급 분당 한도 회피용으로 호출 사이 약간 쉼)
    summaries = []
    active = [(ch, m) for ch, m in data.items() if m]
    for i, (ch, messages) in enumerate(active):
        try:
            s = digest.summarize_channel(ch, messages)
            if s and s != "오늘은 새 메시지 없음":
                summaries.append(s)
        except Exception as e:
            print(f"[요약] ⚠ '{ch}' 1차 요약 실패: {e}")
        if i < len(active) - 1:
            time.sleep(config.SLEEP_BETWEEN_CALLS)

    if not summaries:
        print("\n오늘은 새 메시지 없음")
        return

    # 3) 합치기
    final = digest.merge_summaries(summaries)

    # 4) 출력 + 저장
    print("\n" + "=" * 60)
    print(final)
    print("=" * 60)

    OUT_DIR.mkdir(exist_ok=True)
    stamp = datetime.now(config.TZ).strftime("%Y-%m-%d")
    path = OUT_DIR / f"다이제스트_{stamp}.md"
    path.write_text(final, encoding="utf-8")
    print(f"\n💾 저장됨: {path}")

    # 5) 정시 발송 대기 (SEND_AT 이 지정된 경우, 한국시간 그 시각 정각까지 기다림)
    _wait_until_send_time()

    # 6) 비공개 채널로 전송
    await deliver.send_digest(final)


if __name__ == "__main__":
    asyncio.run(run())
