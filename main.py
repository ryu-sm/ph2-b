from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager


from core.config import settings
from core.log import log_register
from core.database import db_register

from core.custom import AuthException


from apis.routers.users import router as users_router
from apis.routers.optipns import router as optipns_router


# スタートアップ前のイベント
@asynccontextmanager
async def lifespan(app: FastAPI):
    # グローバルログの初期化
    await db_register()
    # データベースプールの初期化
    await log_register()
    yield


# アプリ設定
app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan,
)


# ROUTER追加
app.include_router(users_router)
app.include_router(optipns_router)


# カスタム認証例外追加
@app.exception_handler(AuthException)
async def custom_auth_exception_handler(request: Request, exception: AuthException) -> JSONResponse:
    return JSONResponse(status_code=401, content={"message": "token is invalid."})


# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    from uvicorn import run

    run(app="main:app", host="0.0.0.0", port=8000, reload=True)
