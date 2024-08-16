"""Unittests."""

import datetime
from random import sample

import pytest

from src.schemas import OnlineScoreRequest, ClientsInterestsRequest
from src.scoring import get_score, get_interests
from src.utils import generate_uid


@pytest.mark.parametrize(
    "login, first_name, last_name, email, phone, birthday, gender, expected_result",
    [
        ("not_admin_1", None, None, "stupnikov@otus.ru", "79175002040", None, None, {'score': 3.0}),
        ("not_admin_2", None, None, "stupnikov@otus.ru", 79175002040, None, None, {'score': 3.0}),
        ("not_admin_3", "a", "b", None, None, "01.01.2000", 1, {'score': 2.0}),
        ("not_admin_4", None, None, None, None, "01.01.2000", 0, {'score': 1.5}),
        ("not_admin_5", None, None, None, None, "01.01.2000", 2, {'score': 1.5}),
        ("not_admin_6", "a", "b", None, None, None, None, {'score': 0.5}),
        ("not_admin_7", "a", "b", "stupnikov@otus.ru", "79175002040", "01.01.2000", 1, {'score': 5.0}),
    ],
)
def test_get_score(storage_manager, login, first_name, last_name, email, phone, birthday, gender, expected_result):
    request_data = OnlineScoreRequest(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        birthday=birthday,
        gender=gender,
    )
    key = generate_uid([first_name or "", last_name or "", str(phone) if phone else "", birthday or ""])

    result = get_score(storage_manager, request_data, login=login)

    assert result == expected_result
    assert result.get("score") == float(storage_manager.get_cache(key))

    storage_manager.del_many_data(key)


@pytest.mark.parametrize(
    "login, first_name, last_name, email, phone, birthday, gender, expected_result",
    [
        ("admin", None, None, None, None, None, None, {'score': 42}),
    ],
)
def test_get_admin_score(
        storage_manager, login, first_name, last_name, email, phone, birthday, gender, expected_result
):
    request_data = OnlineScoreRequest(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        birthday=birthday,
        gender=gender,
    )

    result = get_score(storage_manager, request_data, login=login)

    assert result == expected_result


@pytest.mark.parametrize(
    "login, client_ids, date",
    [
        ("not_admin", [1, 2, 3],datetime.datetime.today().strftime("%d.%m.%Y")),
        ("not_admin", [1, 2], "19.07.2017"),
        ("not_admin", [0], None),
    ]
)
def test_get_interests(storage_manager, login, client_ids, date):
    request_data = ClientsInterestsRequest(client_ids=client_ids, date=date)
    interests = ["cars", "pets", "travel", "hi-tech", "sport", "music", "books", "tv", "cinema", "geek", "otus"]
    data_to_insert = {str(client_id): sample(interests, 2) for client_id in client_ids}
    for client_id in data_to_insert:
        storage_manager.set_list_data(client_id, data_to_insert[client_id])

    result = get_interests(storage_manager, request_data, login)

    storage_manager.del_many_data(*data_to_insert.keys())
    assert sorted(list(result.keys())) == list(map(str, client_ids))
    for client_id in result:
        assert sorted(result[client_id]) == sorted(data_to_insert[client_id])


def test_get_admin_interests(storage_manager):
    request_data = ClientsInterestsRequest(client_ids=[0], date="01.01.2000")

    result = get_interests(storage_manager, request_data, "admin")

    assert result == {"admin": ["all"]}
