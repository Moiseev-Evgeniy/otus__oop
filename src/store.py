"""Cache storage module."""

from typing import Any

from redis.client import Redis
from redis.backoff import ExponentialBackoff
from redis.retry import Retry
from redis.exceptions import BusyLoadingError, ConnectionError, TimeoutError

from src.constants import TIMEOUT, RETRY, TTL


class StorageManager:

    client = Redis(
        host="0.0.0.0",
        port=6379,
        socket_timeout=TIMEOUT,
        retry=Retry(ExponentialBackoff(), RETRY),
        retry_on_error=[BusyLoadingError, ConnectionError, TimeoutError],
        decode_responses=True,
    )

    @classmethod
    def get_cache(cls, key: str) -> Any:
        return cls.client.get(key)

    @classmethod
    def set_cache(cls, key: str, value: Any, ttl: int | None = None) -> None:
        cls.client.set(key, value, ex=ttl or TTL)

    # imitating another db
    @classmethod
    def get_data(cls, key: str) -> str:
        return cls.client.get(key)

    @classmethod
    def get_many_data(cls, keys: list[str]) -> list[str]:
        return cls.client.mget(keys)

    @classmethod
    def get_all_list_data(cls, key: str) -> list:
        return cls.client.lrange(key, 0, cls.client.llen(key))

    @classmethod
    def set_data(cls, key: str, value: Any) -> None:
        cls.client.set(key, value)

    @classmethod
    def set_many_data(cls, data: dict[str, Any]) -> None:
        cls.client.mset(data)

    @classmethod
    def set_list_data(cls, key: str, values: list) -> None:
        cls.client.lpush(key, *values)

    @classmethod
    def del_many_data(cls, *args) -> None:
        cls.client.delete(*args)
