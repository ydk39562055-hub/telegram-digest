"""공용 텔레그램 클라이언트 생성기.

- 로컬: 파일 세션(digest.session) 사용
- 클라우드(깃허브 액션): TG_SESSION_STRING 환경변수의 문자열 세션 사용
"""
from telethon import TelegramClient
from telethon.sessions import StringSession

import config


def make_client():
    if config.TG_SESSION_STRING:
        return TelegramClient(
            StringSession(config.TG_SESSION_STRING), config.TG_API_ID, config.TG_API_HASH
        )
    return TelegramClient(config.TG_SESSION, config.TG_API_ID, config.TG_API_HASH)
