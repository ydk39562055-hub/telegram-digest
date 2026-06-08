"""Gemini API 호출부 (멀티모달: 텍스트 + 차트 이미지).

- summarize_channel: 채널 하나의 메시지들 → 1차 요약 (이미지 포함)
- merge_summaries: 채널별 1차 요약들 → 최종 다이제스트
"""
import time

from google import genai
from google.genai import types
from google.genai import errors as genai_errors

import config
import prompts

_client = None


def _get_client():
    global _client
    if _client is None:
        if not config.GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY 가 비어 있다. .env 를 확인하라.")
        _client = genai.Client(api_key=config.GEMINI_API_KEY)
    return _client


def _generate(contents, retries: int = 4):
    """generate_content + 분당 속도제한(429) 자동 재시도(점점 길게 대기)."""
    delay = 20  # 무료 등급 분당 한도에 걸리면 20초부터 백오프
    for attempt in range(retries + 1):
        try:
            resp = _get_client().models.generate_content(
                model=config.GEMINI_MODEL,
                contents=contents,
            )
            return (resp.text or "").strip()
        except genai_errors.APIError as e:
            code = getattr(e, "code", None)
            # 429=속도제한, 503=일시적 → 대기 후 재시도. 그 외는 즉시 실패.
            if code in (429, 503) and attempt < retries:
                print(f"   ⏳ 한도/일시오류({code}) → {delay}초 대기 후 재시도 ({attempt+1}/{retries})")
                time.sleep(delay)
                delay = min(delay * 2, 90)
                continue
            raise


def summarize_channel(channel_name: str, messages: list) -> str:
    """messages: [{time, text, images:[bytes]}] → 1차 요약 문자열."""
    if not messages:
        return ""  # 빈 채널은 호출 자체를 안 함 (가드)

    # contents = [프롬프트, 채널명, 그리고 메시지별로 (텍스트 + 이미지...)]
    contents = [prompts.PER_CHANNEL, f"채널명: {channel_name}"]
    for m in messages:
        block = f"--- {m['time']} ---\n{m['text']}".strip()
        contents.append(block)
        for img in m["images"]:
            contents.append(types.Part.from_bytes(data=img, mime_type="image/jpeg"))

    # --- 점검 4: Gemini로 실제 넘어가는 내용 확인 ---
    n_img = sum(len(m["images"]) for m in messages)
    print(f"[점검4] '{channel_name}' → Gemini 전달: 텍스트블록 {len(messages)}개, 이미지 {n_img}장")

    return _generate(contents)


def merge_summaries(summaries: list[str]) -> str:
    """채널별 1차 요약 리스트 → 최종 다이제스트 문자열."""
    joined = "\n\n".join(s for s in summaries if s.strip())
    if not joined.strip():
        return "오늘은 새 메시지 없음"  # 코드 레벨 가드

    contents = [prompts.EDITOR, joined]
    print(f"[점검4] 최종 합치기 → Gemini 전달: 1차요약 {len(summaries)}개, 총 {len(joined)}자")

    return _generate(contents)
