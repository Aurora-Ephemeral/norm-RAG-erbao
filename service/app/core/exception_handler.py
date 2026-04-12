from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

def register_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": exc.status_code,
                "message": exc.detail,
                "data": None,
                "success": False,
                },
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "code": 422,
                "message": "Request validation error",
                "data": exc.errors(),
                "success": False,
            },
        )
    
    
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "message": "Internal server error",
                "data": None,
                "success": False,
            },
        )