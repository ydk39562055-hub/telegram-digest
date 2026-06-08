# 텔레그램 투자채널 다이제스트 (클라우드 자동)

텔레그램 **"메크로 분석" 폴더**의 채널들에서 **최근 24시간 글(텍스트+차트)** 을 모아,
Gemini로 채널별 요약 → 전체 합치기 한 뒤 **비공개 채널 "📊 투자 다이제스트"** 로 보낸다.

- **매일 17:00(한국시간) 시작 → 18:00 정각 발송** (계산을 미리 끝내두고 정각에 쏨)
- **깃허브 액션(클라우드)** 에서 실행 → PC 안 켜져 있어도 돌아감
- 채널 목록은 텔레그램 "메크로 분석" 폴더 기준 **자동** (폴더에서 넣고/빼면 그대로 반영)

저장소: https://github.com/ydk39562055-hub/telegram-digest (공개 — 액션 무료시간 무제한)

## 동작 흐름
1. `fetch.py` — "메크로 분석" 폴더의 채널들에서 최근 24시간 글 수집
2. `digest.py` — 채널별 1차 요약(Gemini, 차트 이미지 포함) → 전체 합치기
3. `deliver.py` — 비공개 채널로 전송(4096자 넘으면 나눠 보냄)
4. `main.py` — 위를 순서대로, 그리고 18:00 정각까지 기다렸다가 발송

## 채널을 바꾸고 싶을 때
텔레그램 앱에서 **"메크로 분석" 폴더**에 채널을 추가/삭제만 하면 끝. 코드/설정 수정 불필요.
(다른 폴더로 바꾸려면 깃허브 시크릿 `FOLDER` 값을 그 폴더 이름으로 변경.)

## 시간/발송 시각을 바꾸고 싶을 때
- 발송 시각: 깃허브 시크릿이 아니라 워크플로 파일 `.github/workflows/digest.yml` 의
  `SEND_AT`(기본 18:00)과 `cron`(기본 08:00 UTC=17:00 KST) 수정.

## 클라우드 비밀값(깃허브 시크릿)
저장소 Settings → Secrets → Actions 에 등록돼 있음:
`TG_API_ID`, `TG_API_HASH`, `TG_SESSION_STRING`, `GEMINI_API_KEY`, `FOLDER`, `DEST_CHANNEL`

## 수동 테스트
- 깃허브 저장소 → Actions → telegram-digest → **Run workflow**
  → "즉시 발송" 체크하면 18:00 안 기다리고 바로 보냄.
- CLI: `gh workflow run digest.yml --field send_now=true`

## 로컬에서 직접 돌려볼 때 (선택)
1. `pip install -r requirements.txt`
2. `.env.example` 복사 → `.env` 채우기 (`my.telegram.org` 키, Gemini 키, `FOLDER` 등)
3. 최초 로그인: `python login_helper.py send "+82..."` → `python login_helper.py code 12345`
4. 실행: `python main.py`  (로컬에선 `SEND_AT` 비우면 즉시 발송)

## 보조 스크립트
- `login_helper.py` — 비대화식 로그인(코드 발송/입력 2단계)
- `list_channels.py` — 구독 채널 전체 목록 + 아이디
- `list_folders.py` — 채팅 폴더별 채널 묶음
- `create_dest_channel.py` — 받을 비공개 채널 생성(1회)
- `export_session.py` — 파일세션 → 문자열세션(클라우드 시크릿용)
- `check_env.py` — .env 형식 점검

## 파일별 점검 로그
실행하면 `[수집범위] / [점검2 로그인] / [점검3 채널별 개수] / [점검4 Gemini 전달] / [전송]`
순서로 상태가 찍혀, 어디서 멈췄는지 바로 보인다.
