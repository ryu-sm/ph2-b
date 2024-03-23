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
from apis.routers.tools import router as tools_router
from apis.routers.optipns import router as optipns_router
from apis.routers.orgs import router as orgs_router
from apis.routers.apply import router as apply_router
from apis.routers.managers import router as managers_router
from apis.routers.sales_persons import router as sales_persons_router
from apis.routers.preliminaries import router as preliminaries_router
from apis.routers.c_archive_files import router as c_archive_files_router
from apis.routers.messages import router as messages_router


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
app.include_router(tools_router)
app.include_router(users_router)
app.include_router(optipns_router)
app.include_router(orgs_router)
app.include_router(apply_router)
app.include_router(managers_router)
app.include_router(sales_persons_router)
app.include_router(preliminaries_router)
app.include_router(c_archive_files_router)
app.include_router(messages_router)


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
