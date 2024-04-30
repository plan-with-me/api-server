import os
import sys
import logging
import importlib

from tortoise import Tortoise
from fastapi.middleware.cors import CORSMiddleware

from core.config import secrets
from main import app


origins = [
    "http://localhost:3000",
    # TODO Add client origin
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


import core.exception_handler


router_modules, model_modules = [], []
for app_name in os.listdir("apps"):
    for module_name in os.listdir(f"apps/{app_name}"):
        if module_name == "router.py":
            router_modules.append(f"apps.{app_name}.router")
        elif module_name == "model.py":
            model_modules.append(f"apps.{app_name}.model")

for router_module in router_modules:
    module = importlib.import_module(router_module)
    if hasattr(module, "router"):
        app.include_router(module.router)


db_config = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.asyncpg",
            "credentials": {
                "host": secrets.DB_HOST,
                "port": secrets.DB_PORT,
                "user": secrets.DB_USER,
                "password": secrets.DB_PASSWORD,
                "database": secrets.DB_DATABASE,
                "schema": secrets.DB_SCHEMA,
            },
        },
    },
    "apps": {
        "models": {
            "models": model_modules,
            "default_connection": "default",
        },
    },
}

@app.on_event("startup")
async def on_start_up():
    await Tortoise.init(
        config=db_config,
        use_tz=True,
        timezone="Asia/Seoul",
    )

    from core import init_db
    await init_db.schema_and_tables(safe=False)

    # Get tortoise logger for debug sql script
    fmt = logging.Formatter(fmt="%(message)s\n", datefmt="%Y-%m-%d %H:%M:%S")
    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(logging.DEBUG)
    sh.setFormatter(fmt)

    logger_db_client = logging.getLogger("tortoise.db_client")
    logger_db_client.setLevel(logging.DEBUG)
    logger_db_client.addHandler(sh)
