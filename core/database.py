import typing
import aiomysql
from loguru import logger
from core.config import settings


class DB:
    _instance = None

    def __new__(cls, *args, **kw):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kw)
        return cls._instance

    def __init__(self) -> None:
        self._pool = None

    async def connect(self) -> None:
        if self._pool is None:
            self._pool = await aiomysql.create_pool(
                user=settings.DB_USER,
                password=settings.DB_PASSWORD,
                db=settings.DB_NAME,
                host=settings.DB_HOST,
                port=settings.DB_PORT,
                autocommit=True,
            )

    async def fetch_one(self, sql) -> typing.Optional[aiomysql.DictCursor]:
        if self._pool is None:
            await self.connect()
        async with self._pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                if settings.APP_DEBUG:
                    logger.info(sql)
                await cur.execute(sql)
                result = await cur.fetchone()
                return result

    async def fetch_all(self, sql) -> typing.List[aiomysql.DictCursor]:
        if self._pool is None:
            await self.connect()
        async with self._pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                if settings.APP_DEBUG:
                    logger.info(sql)
                await cur.execute(sql)
                result = await cur.fetchall()
                return result

    async def execute(self, sql) -> None:
        if self._pool is None:
            await self.connect()
        async with self._pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                if settings.APP_DEBUG:
                    logger.info(sql)
                await cur.execute(sql)
                await conn.commit()

    async def uuid_short(self) -> int:
        result = await self.fetch_one("SELECT UUID_SHORT() AS value;")
        return result["value"]


async def db_register():
    db = DB()
    await db.connect()
