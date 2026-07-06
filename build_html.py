"""최종 다이제스트 텍스트 → 허브(invest-hub)와 같은 다크 디자인의 웹페이지(docs/index.html).

- 다이제스트는 `@@@` 로 주제 블록이 나뉘어 있다(prompts.STYLE 규칙).
  각 블록의 첫 줄 = 제목(이모지 포함), 나머지 = `- ` 항목들.
- 이 파일이 블록을 카드로, 항목을 리스트로 렌더한다.
- 허브가 iframe 으로 이 페이지를 띄운다 → 색/폰트 토큰을 허브와 동일하게 맞춤.
"""
import html
from datetime import datetime
from pathlib import Path

DOCS = Path(__file__).resolve().parent / "docs"

# 허브(invest-hub/index.html)와 동일한 통일 다크 토큰
_HEAD = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>뉴스 다이제스트</title>
<link rel="preconnect" href="https://cdn.jsdelivr.net">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable.min.css">
<style>
  /* 브라운 리디자인 토큰 (handoff_브라운_대시보드) */
  :root{--bg:#15100d;--bar:#120e0b;--panel:#221b15;--panel2:#261e16;--line:#3a2f24;
    --txt:#f2ebe0;--mut:#a08f7d;--accent:#c89468}
  *{box-sizing:border-box}
  html,body{margin:0}
  body{background:var(--bg);color:var(--txt);
    font-family:'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic',system-ui,sans-serif;
    -webkit-font-smoothing:antialiased;line-height:1.6}
  .wrap{max-width:820px;margin:0 auto;padding:22px 16px 60px}
  header.top{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap;
    padding-bottom:14px;margin-bottom:18px;border-bottom:1px solid var(--line)}
  header.top h1{font-size:19px;font-weight:800;letter-spacing:-.3px;margin:0;display:flex;align-items:center;gap:8px}
  header.top h1 .dot{width:8px;height:8px;border-radius:2px;background:var(--accent);display:inline-block}
  header.top .when{color:var(--mut);font-size:12.5px}
  .card{background:var(--panel);border:1px solid var(--line);border-radius:14px;
    padding:14px 16px;margin:0 0 14px}
  .card h2{font-size:15px;font-weight:700;margin:0 0 10px;letter-spacing:-.2px}
  .card.lead{background:var(--panel2);border-color:#7c5e3f}
  .card.lead h2{color:var(--accent)}
  .card.warn{border-color:#5a4630}
  ul{margin:0;padding:0;list-style:none}
  li{position:relative;padding:6px 0 6px 16px;border-top:1px solid transparent}
  li+li{border-top:1px solid #2a2118}
  li::before{content:"";position:absolute;left:2px;top:14px;width:5px;height:5px;
    border-radius:50%;background:var(--accent);opacity:.75}
  .card.lead li::before{background:var(--accent);opacity:1}
  .t{color:var(--mut);font-variant-numeric:tabular-nums;font-size:12.5px;margin-right:4px}
  .empty{color:var(--mut);text-align:center;padding:60px 0;font-size:14px}
  .foot{color:var(--mut);font-size:11.5px;text-align:center;margin-top:24px}
  @media(max-width:520px){.wrap{padding:16px 12px 48px} header.top h1{font-size:17px}}
</style>
</head>
<body>
<div class="wrap">
"""

_FOOT = """  <div class="foot">텔레그램 투자채널 다이제스트 · 자동 생성 · 원문 요약(투자 조언 아님)</div>
</div>
</body>
</html>
"""


def _card_class(title: str) -> str:
    """제목으로 카드 강조 종류 판별."""
    if "한눈에" in title:
        return "card lead"
    if "확인 필요" in title or "확인필요" in title:
        return "card warn"
    return "card"


def _render_item(line: str) -> str:
    """'- HH:MM  내용' 한 줄을 <li> 로. 앞의 시간(HH:MM)이 있으면 회색으로 뺀다."""
    s = line.lstrip("-•*  ").rstrip()
    s = s.replace("**", "").strip()  # 모델이 가끔 넣는 굵게(**) 마크다운 제거
    if not s:
        return ""
    # 맨 앞이 'HH:MM' 형태면 시간 배지로 분리
    head, rest = "", s
    parts = s.split(None, 1)
    if parts and len(parts[0]) == 5 and parts[0][2] == ":" and parts[0].replace(":", "").isdigit():
        head = f'<span class="t">{html.escape(parts[0])}</span>'
        rest = parts[1] if len(parts) > 1 else ""
    return f"<li>{head}{html.escape(rest)}</li>"


def _render_block(block: str) -> str:
    lines = [ln for ln in block.splitlines() if ln.strip()]
    if not lines:
        return ""
    title = lines[0].replace("**", "").replace("#", "").strip()
    items = []
    for ln in lines[1:]:
        li = _render_item(ln)
        if li:
            items.append("    " + li)
    body = "\n".join(items) if items else '    <li style="opacity:.6">특이사항 없음</li>'
    return (f'  <section class="{_card_class(title)}">\n'
            f'    <h2>{html.escape(title)}</h2>\n'
            f'    <ul>\n{body}\n    </ul>\n'
            f'  </section>')


def render(text: str, when: datetime | None = None) -> str:
    when = when or datetime.now()
    when_str = when.strftime("%Y-%m-%d %H:%M")
    header = ('<header class="top">'
              '<h1><span class="dot"></span>뉴스 다이제스트</h1>'
              f'<span class="when">업데이트 {html.escape(when_str)} · 최근 24시간</span>'
              '</header>\n')

    text = (text or "").strip()
    if not text or text == "오늘은 새 메시지 없음":
        return _HEAD + header + '  <div class="empty">오늘은 새 메시지 없음</div>\n' + _FOOT

    blocks = [b for b in (b.strip() for b in text.split("@@@")) if b]
    cards = "\n".join(c for c in (_render_block(b) for b in blocks) if c)
    return _HEAD + header + cards + "\n" + _FOOT


def write(text: str, when: datetime | None = None) -> Path:
    """docs/index.html 로 저장하고 경로 반환."""
    DOCS.mkdir(exist_ok=True)
    out = DOCS / "index.html"
    out.write_text(render(text, when), encoding="utf-8")
    return out


if __name__ == "__main__":  # 로컬 테스트: 가장 최근 저장된 다이제스트로 페이지 생성
    import sys
    src = Path(__file__).resolve().parent / "출력"
    mds = sorted(src.glob("다이제스트_*.md")) if src.exists() else []
    sample = mds[-1].read_text(encoding="utf-8") if mds else "오늘은 새 메시지 없음"
    p = write(sample)
    print(f"작성됨: {p}  (source: {mds[-1].name if mds else '없음(placeholder)'})")
    sys.exit(0)
