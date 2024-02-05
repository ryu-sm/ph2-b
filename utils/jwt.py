from jose import jwt
from datetime import datetime, timedelta
from core.config import settings


def gen_token(payload: dict, expires_delta: int = settings.JWT_VERIFY_EMAIL_TOKEN_EXP) -> str:
    exp = datetime.utcnow() + timedelta(minutes=expires_delta)
    return jwt.encode(
        claims={**payload, "exp": exp},
        key=settings.JWT_SECRETS_KEY,
        algorithm=settings.JWT_ALGORITHM,
        headers={"alg": settings.JWT_ALGORITHM, "type": "JWT"},
    )


def parse_token(token):
    try:
        payload = jwt.decode(
            token=token,
            key=settings.JWT_SECRETS_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except Exception:
        return None


def only_parse_payload(token):
    try:
        return jwt.decode(
            token=token,
            key=settings.JWT_SECRETS_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_exp": False},
        )
    except Exception:
        return None
