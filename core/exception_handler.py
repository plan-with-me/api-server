from fastapi import Request, status
from fastapi.responses import JSONResponse

from tortoise.exceptions import IntegrityError, DoesNotExist

from main import app


@app.exception_handler(Exception)
async def handle_unexpected_exceptions(request: Request, exc: Exception):
    # TODO handle exception code

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": exc.__class__.__name__,
            "detail": str(exc),
            "metadata": {
                "request_info": {
                    "method": request.method, 
                    "hostname": request.url.hostname, 
                    "port": request.url.port,
                    "path_params": request.url.path,
                    "query_params": request.url.query,
                    "headers": {
                        header[0]: header[1] 
                        for header in request.headers.items()
                    },
                },
            },
        }
    )
