"""Business logic module."""

import logging

from src.schemas import OnlineScoreRequest, ClientsInterestsRequest
from src.store import StorageManager
from src.utils import generate_uid


def get_score(store: StorageManager, request_data: OnlineScoreRequest, login: str) -> dict:
    """The method of calculating the user's rating."""

    if login == "admin":
        return {"score": 42}

    if request_data.phone and isinstance(request_data.phone, int):
        request_data.phone = str(request_data.phone)

    key_parts = [
        request_data.first_name or "",
        request_data.last_name or "",
        request_data.phone or "",
        request_data.birthday or "",
    ]
    key = generate_uid(key_parts)

    try:
        if (cache_score := store.get_cache(key)) is not None:
            return {"score": float(cache_score)}
    except:
        logging.exception("Connection to cache storage failed.")

    score = 0
    if request_data.phone:
        score += 1.5
    if request_data.email:
        score += 1.5
    if request_data.birthday and request_data.gender is not None:
        score += 1.5
    if request_data.first_name and request_data.last_name:
        score += 0.5

    try:
        store.set_cache(key, score)
    except:
        logging.exception("Connection to cache storage failed.")

    return {"score": score}


def get_interests(store: StorageManager, request_data: ClientsInterestsRequest, login: str) -> dict:
    """The method of providing the user's hobbies."""

    if login == "admin":
        return {"admin": ["all"]}

    return {str(client_id): store.get_all_list_data(str(client_id)) for client_id in request_data.client_ids}

