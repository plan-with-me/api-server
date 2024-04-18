from fastapi import FastAPI, status
from fastapi.responses import RedirectResponse


app = FastAPI(
    title="Plan with me",
    root_path="/api",
    docs_url='/docs',
    redoc_url='/redoc',
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