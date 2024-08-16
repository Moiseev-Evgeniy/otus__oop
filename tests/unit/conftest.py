"""Pytest fixtures."""

import pytest

from tests.unit.utils import MockStorageManager


@pytest.fixture()
def mock_storage_manager():
    yield MockStorageManager
