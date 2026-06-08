# 텔레그램 투자채널 다이제스트 (자동)

여러 텔레그램 투자 채널의 **최근 24시간 글(텍스트 + 차트 이미지)** 을 자동으로 가져와,
Gemini로 채널별 요약 → 전체 합치기 해서 **출근길 폰용 다이제스트**를 만든다.
사람이 글을 붙여넣는 단계는 없다. 가져온 게 없으면 그냥 "오늘은 새 메시지 없음" 만 나온다.

## 처음 한 번만 하는 준비

1. **파이썬 라이브러리 설치**
   - 이 폴더에서 명령창을 열고:
     ```
     pip install -r requirements.txt
     ```

2. **텔레그램 API 키 발급**
   - 인터넷에서 `my.telegram.org` 접속 → 로그인 → `API development tools` 클릭
   - `App title` 아무거나 입력 → 만들면 **api_id**(숫자)와 **api_hash**(긴 문자열)가 나온다.

3. **Gemini 키 발급**
   - `aistudio.google.com/app/apikey` 접속 → `Create API key` 클릭 → 키 복사.

4. **설정 파일 만들기**
   - 이 폴더의 `.env.example` 파일을 복사해서 이름을 `.env` 로 바꾼다.
   - 메모장으로 열어서 빈칸을 채운다:
     - `TG_API_ID` = 위에서 받은 숫자
     - `TG_API_HASH` = 위에서 받은 문자열
     - `GEMINI_API_KEY` = Gemini 키
     - `CHANNELS` = 요약할 채널들. 쉼표로 구분.
       예) `CHANNELS=@channel_a,@channel_b`
       (채널 username이 없으면 채널 숫자ID `-100...` 도 가능)

5. **텔레그램 로그인 (최초 1회)**
   ```
   python login.py
   ```
   - 전화번호(+82...)와 텔레그램 앱으로 온 인증코드를 입력하면
   - `digest.session` 파일이 생긴다. 이후로는 다시 로그인 안 해도 된다.

## 매일 실행

```
python main.py
```
- 결과가 화면에 뜨고, `출력/다이제스트_YYYY-MM-DD.md` 로도 저장된다.

## 안 될 때 (화면에 점검 로그가 찍힌다)

실행하면 단계별로 상태가 출력된다. 막히는 지점을 그대로 보면 된다:

- `[점검1] CHANNELS = []` → `.env` 의 CHANNELS 가 비었음. 채널을 채워라.
- `[점검2] Telethon 세션 로그인됨? False` → `python login.py` 를 먼저 실행.
- `[점검3] @채널: 메시지 0개` → 그 채널에 최근 24시간 글이 없거나, 접근 권한 없음(가입 안 한 비공개 채널 등).
- `[점검4] ... Gemini 전달: ...` → fetch 결과가 Gemini로 잘 넘어가는 중.
- 전부 0개면 마지막에 `오늘은 새 메시지 없음` 만 출력된다(정상 동작).

## 파일 설명
- `config.py` — `.env` 값 로딩
- `login.py` — 최초 1회 텔레그램 로그인
- `fetch.py` — 채널 최근 24시간 글 가져오기 (점검 1·2·3 로그)
- `prompts.py` — 1차/2차 프롬프트 + 빈 입력 가드
- `digest.py` — Gemini 호출 (점검 4 로그)
- `main.py` — 전체 실행 + 저장
