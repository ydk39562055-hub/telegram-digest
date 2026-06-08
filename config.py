"""환경설정 로딩. .env 파일에서 값을 읽어온다."""
import os
from pathlib import Path
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

# 이 파일이 있는 폴더 = 프로젝트 폴더. 어느 위치에서 실행해도 .env/세션을 찾도록 절대경로 고정.
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def _as_int(name: str, default: int = 0) -> int:
    """숫자가 아니면(자리표시자 등) 죽지 않고 default로."""
    raw = (os.getenv(name, "") or "").strip()
    try:
        return int(raw)
    except ValueError:
        return default


def _as_bool(name: str, default: bool = False) -> bool:
    raw = (os.getenv(name, "") or "").strip().lower()
    if raw in ("1", "true", "y", "yes", "on"):
        return True
    if raw in ("0", "false", "n", "no", "off"):
        return False
    return default


# 시간대는 한국시간으로 고정(클라우드 서버는 기본 UTC라서 명시 필요)
TZ = ZoneInfo(os.getenv("TZ_NAME", "Asia/Seoul"))


TG_API_ID = _as_int("TG_API_ID", 0)
TG_API_HASH = os.getenv("TG_API_HASH", "")
# 세션 파일도 프로젝트 폴더에 고정 생성(실행 위치 무관)
TG_SESSION = str(BASE_DIR / os.getenv("TG_SESSION", "digest"))
# 클라우드(깃허브 액션)용: 파일 세션 대신 문자열 세션. 있으면 이걸 우선 사용.
TG_SESSION_STRING = os.getenv("TG_SESSION_STRING", "").strip()
# 다이제스트를 보낼 비공개 채널 id (예: -1001234567890). 비우면 전송 안 함.
DEST_CHANNEL = os.getenv("DEST_CHANNEL", "").strip()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# FOLDER 가 지정되면 그 텔레그램 채팅 폴더의 채널을 자동으로 쓴다(CHANNELS 무시).
FOLDER = os.getenv("FOLDER", "").strip()

# "@a, @b" -> ["@a", "@b"]  (빈 항목/공백 제거). FOLDER 없을 때만 사용.
CHANNELS = [c.strip() for c in os.getenv("CHANNELS", "").split(",") if c.strip()]

# 수집 범위: 오늘 0시(자정)부터 지금까지. 끄면 HOURS(최근 N시간) 사용.
SINCE_MIDNIGHT = _as_bool("SINCE_MIDNIGHT", True)
HOURS = _as_int("HOURS", 24)
# 정시 발송 시각("HH:MM", 한국시간). 비우면 계산 끝나는 즉시 발송.
SEND_AT = os.getenv("SEND_AT", "").strip()
MAX_IMAGES_PER_CHANNEL = _as_int("MAX_IMAGES_PER_CHANNEL", 12)
# 무료 등급 분당 한도 회피용: 채널 요약 호출 사이 대기(초)
SLEEP_BETWEEN_CALLS = _as_int("SLEEP_BETWEEN_CALLS", 4)
