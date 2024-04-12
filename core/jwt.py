import jwt
import pytz
from datetime import datetime, timedelta

import core.config.var_config as vars
import core.config.secrets as secrets


def build_token(**kwargs) -> str:
    current_time = datetime.now(pytz.timezone("Asia/Seoul"))
    payload = {
        "iss": vars.ISSUER,
        "iat": current_time,
        "exp": current_time + timedelta(seconds=vars.TOKEN_DURATION),
    }
    payload.update(kwargs)

    return jwt.encode(
        payload=payload,
        key=secrets.JWT_ENCRYPTION_KEY,
        algorithm=vars.ALG,
    )


def decode_token(token: str) -> dict:
    return jwt.decode(
        jwt=token,
        issuer=vars.ISSUER,
        key=secrets.JWT_ENCRYPTION_KEY,
        algorithms=vars.ALG,
        verify=True,
        options={
            "verify_signature": True,
        },
    )
