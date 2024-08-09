"""Business logic module."""

import random

from schemas import OnlineScoreRequest, ClientsInterestsRequest


def get_score(request_data: OnlineScoreRequest, login: str) -> dict:
    """The method of calculating the user's rating."""

    if login == "admin":
        return {"score": 42}

    score = 0
    if request_data.phone:
        score += 1.5
    if request_data.email:
        score += 1.5
    if request_data.birthday and request_data.gender:
        score += 1.5
    if request_data.first_name and request_data.last_name:
        score += 0.5
    return {"score": score}


def get_interests(request_data: ClientsInterestsRequest, login: str) -> dict:
    """The method of providing the user's hobbies."""

    interests = ["cars", "pets", "travel", "hi-tech", "sport", "music", "books", "tv", "cinema", "geek", "otus"]
    return {client_id: random.sample(interests, 2) for client_id in request_data.client_ids}
