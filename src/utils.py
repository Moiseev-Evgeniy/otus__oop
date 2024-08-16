"""Utils module."""

import datetime
import hashlib
import logging

from src.constants import SALT, ADMIN_SALT
from src.schemas import MethodRequest


def get_auth_data(request: dict):
    """Method for validating authorization data."""

    try:
        auth_data = MethodRequest(
            account=request.get("account"),
            login=request.get("login"),
            token=request.get("token"),
            arguments=request.get("arguments"),
            method=request.get("method"),
        )
    except AttributeError as e:
        logging.exception("Attribute error: %s" % e)
        auth_data = None
    except ValueError as e:
        logging.exception("Value error: %s" % e)
        auth_data = None

    return auth_data


def check_auth(auth_data):
    """The method for verifying the token."""

    if auth_data.is_admin:
        digest = hashlib.sha512((datetime.datetime.now().strftime("%Y%m%d%H") + ADMIN_SALT).encode('utf-8')).hexdigest()
    else:
        digest = hashlib.sha512((auth_data.account + auth_data.login + SALT).encode('utf-8')).hexdigest()
    return digest == auth_data.token


def is_online_score_request_valid(online_score_request):
    """Method for verifying the sufficiency of information for calculating the rating."""

    if (
            online_score_request.phone is not None and online_score_request.email is not None or
            online_score_request.first_name is not None and online_score_request.last_name is not None or
            online_score_request.gender is not None and online_score_request.birthday is not None
    ):
        return True
    return False


def generate_uid(values: list) -> str:
    return "uid:" + hashlib.md5("".join(values).encode('utf-8')).hexdigest()
