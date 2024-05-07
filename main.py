from fastapi import FastAPI, status
from fastapi.responses import RedirectResponse


app_description = """
### Plan with me API 문서입니다.

**요구 사항**
- 데이터를 포함하여 요청 시 **Content-Type** 헤더의 값을 **application/json** 으로 하여 요청합니다.
- 인증이 필요한 API는 **Authorization** 헤더의 값을 **<auth_type> <access_token>** 으로 하여 요청합니다.
- 문서에서 API 테스트 시 인증이 필요한 API는 우측의 **Authorize** 버튼을 누르고 액세스 토큰 값을 입력한 후 테스트합니다.
"""
app = FastAPI(
    title="Plan with me API",
    root_path="/api",
    docs_url='/docs',
    redoc_url='/redoc',
    contact={
        "email": "iee785@dongyang.ac.kr",
    },

    description=app_description,
)


import core.config.app_config


# Util paths
@app.get("", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse("/api/docs")


@app.get(
    path="/health", 
    status_code=status.HTTP_200_OK, 
    include_in_schema=False
)
async def health_check():
    return "OK"


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app="main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )