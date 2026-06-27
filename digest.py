"""Gemini API 호출부 (멀티모달: 텍스트 + 차트 이미지).

무료 등급은 하루 호출 '횟수'가 빡빡(약 20회)하므로, 채널마다 따로 부르지 않고
모든 채널을 묶어 한 번(또는 소수 묶음)에 호출한다. (이미지 개수는 호출 횟수와 무관)

- make_digest: 전 채널 원문 → 최종 다이제스트 (기본 1회 호출)
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


def _generate(contents):
    """모델 폴백 체인으로 호출. 한 모델이 한도(429)면 다음 모델로 넘어간다.
    무료 한도는 모델별로 별도라, 체인을 두면 하루 가용량이 모델 수만큼 늘어난다."""
    last_err = None
    for model in config.GEMINI_MODELS:
        for attempt in range(2):  # 503 같은 일시 오류만 1회 짧게 재시도
            try:
                resp = _get_client().models.generate_content(model=model, contents=contents)
                if model != config.GEMINI_MODELS[0]:
                    print(f"   ↪ '{model}' 모델로 성공")
                return (resp.text or "").strip()
            except genai_errors.APIError as e:
                code = getattr(e, "code", None)
                last_err = e
                if code == 503 and attempt == 0:
                    print(f"   ⏳ {model} 일시오류(503) → 10초 후 재시도")
                    time.sleep(10)
                    continue
                # 429(한도 소진) 또는 재시도 후에도 실패 → 다음 모델로
                msg = (getattr(e, "message", None) or str(e)).replace("\n", " ")
                print(f"   ⚠ {model} 실패(code={code}) {msg[:300]} → 다음 모델 시도")
                break
    raise last_err


def _build_contents(prompt: str, batch: list, img_cap: int):
    """batch: [(채널명, messages)] → Gemini contents 리스트(텍스트+이미지 인터리브)."""
    contents = [prompt]
    used = 0
    for name, messages in batch:
        contents.append(f"### 채널: {name}")
        for m in messages:
            contents.append(f"--- {m['time']} ---\n{m['text']}".strip())
            for img in m["images"]:
                if used < img_cap:
                    contents.append(types.Part.from_bytes(data=img, mime_type="image/jpeg"))
                    used += 1
    return contents, used


def make_digest(data: dict) -> str:
    """data: {채널명: [messages]} → 최종 다이제스트 문자열.

    기본은 전 채널을 한 번에 호출(1회). CHANNELS_PER_BATCH 가 0보다 크면
    그 크기로 묶어서 묶음별 호출 후 합친다(묶음수+1회)."""
    active = [(n, m) for n, m in data.items() if m]
    if not active:
        return "오늘은 새 메시지 없음"

    size = config.CHANNELS_PER_BATCH or len(active)  # 0 = 전부 한 묶음
    batches = [active[i:i + size] for i in range(0, len(active), size)]

    # 한 묶음(=한방 호출): COMBINED 로 바로 최종 다이제스트
    if len(batches) == 1:
        contents, nimg = _build_contents(prompts.COMBINED, batches[0], config.MAX_IMAGES_TOTAL)
        print(f"[점검4] 한방 호출 → Gemini: 채널 {len(active)}개, 이미지 {nimg}장 (1회 호출)")
        return _generate(contents)

    # 여러 묶음: 묶음별 부분 다이제스트 → 마지막에 합치기
    partials = []
    for i, b in enumerate(batches):
        contents, nimg = _build_contents(prompts.COMBINED, b, config.MAX_IMAGES_TOTAL)
        print(f"[점검4] 묶음 {i+1}/{len(batches)} → Gemini: 채널 {len(b)}개, 이미지 {nimg}장")
        partials.append(_generate(contents))
        if i < len(batches) - 1:
            time.sleep(config.SLEEP_BETWEEN_CALLS)

    joined = "\n\n".join(p for p in partials if p.strip())
    if not joined.strip():
        return "오늘은 새 메시지 없음"
    print(f"[점검4] 합치기 → Gemini: 묶음 {len(partials)}개 (1회 호출)")
    return _generate([prompts.EDITOR, joined])
