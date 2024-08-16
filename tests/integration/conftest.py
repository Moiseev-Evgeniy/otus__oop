"""Pytest fixtures."""

import pytest

from src.store import StorageManager


@pytest.fixture()
def storage_manager():
    yield StorageManager
