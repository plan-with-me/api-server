"""
App variables
"""

import os


SERVER_HOST = "https://pwm.ssc.co.kr"

BASE_STATIC_FILE_LOC = f"{SERVER_HOST}/static"

IS_PROD = True if os.getenv("USER") == "pwm" else False

# JWT
ALG = "HS256"
ISSUER = SERVER_HOST
TOKEN_TYPE = "Bearer"
TOKEN_DURATION = 60 * 60 * 24
