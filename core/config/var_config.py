"""
App variables
"""


SERVER_HOST = "https://pwm.ssc.co.kr"

BASE_STATIC_FILE_LOC = f"{SERVER_HOST}/static"

# JWT
ALG = "HS256"
ISSUER = SERVER_HOST
TOKEN_TYPE = "Bearer"
TOKEN_DURATION = 60 * 60 * 24
