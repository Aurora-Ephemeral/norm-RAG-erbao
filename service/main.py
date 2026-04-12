from fastapi import FastAPI

from app.api.main import api_router
from app.core.exception_handler import register_exception_handlers

app = FastAPI()
register_exception_handlers(app)
app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app="main:app", host="127.0.0.1", port=3000, reload=True)
