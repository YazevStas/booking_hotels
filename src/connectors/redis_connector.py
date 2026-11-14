import logging

import redis.asyncio as redis


class RedisManager:

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self._redis: redis.Redis | None = None

    @property
    def redis(self) -> redis.Redis:
        if self._redis is None:
            raise RuntimeError("Redis не подключен, сначала вызовите connect()")
        return self._redis

    async def connect(self):
        logging.info(f"Начинаю подключение к Redis host={self.host}, port={self.port}")
        self._redis = await redis.Redis(host=self.host, port=self.port)
        logging.info(f"Успешное подключение к Redis host={self.host}, port={self.port}")

    async def set(self, value: str, key: str, expire: int | None = None):
        if expire:
            await self.redis.set(name=key, value=value, ex=expire)
        else:
            await self.redis.set(name=key, value=value)

    async def get(self, key: str):
        return await self.redis.get(name=key)

    async def delete(self, key: str):
        return await self.redis.delete(key)

    async def close(self):
        if self._redis:
            await self._redis.aclose()
