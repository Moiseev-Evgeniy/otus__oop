from typing import Any

from src.store import StorageManager


class MockStorageManager(StorageManager):

    client = {}

    @classmethod
    def get_cache(cls, key: str) -> Any:
        return cls.client.get(key)

    @classmethod
    def set_cache(cls, key: str, value: Any, ttl: int | None = None) -> None:
        cls.client[key] = value

    @classmethod
    def set_list_data(cls, key: str, values: list) -> None:
        cls.client[key] = values

    @classmethod
    def get_all_list_data(cls, key: str) -> Any:
        return cls.client.get(key)
