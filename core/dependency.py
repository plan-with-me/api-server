from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer
from jwt.exceptions import PyJWTError

import core.config.var_config as vars
from core.jwt import decode_token


class Auth(HTTPBearer):

    def __init__(self):
        super(Auth, self).__init__()

    async def __call__(self, request: Request):
        auth_header = request.headers.get("Authorization", None)

        if not auth_header:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED)

        try:
            token_type, token = auth_header.split(" ")
        except ValueError:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED)

        if token_type != vars.TOKEN_TYPE:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED)

        try:
            token_payload = decode_token(token)
            request.state.token_payload = token_payload
        except PyJWTError as e:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED)
