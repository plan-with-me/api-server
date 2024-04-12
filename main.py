from fastapi import FastAPI


app = FastAPI(
    title="TODO",
    docs_url='/docs',
    redoc_url='/redoc',
)

import core.config.app_config


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app="main:app",
        port=8000,
        reload=True,
    )