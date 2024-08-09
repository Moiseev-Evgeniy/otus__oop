#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Main entrypoint."""


import json
import logging
import uuid
from argparse import ArgumentParser
from http.server import BaseHTTPRequestHandler, HTTPServer
from email.message import Message

from constants import INVALID_REQUEST, NOT_FOUND, INTERNAL_ERROR, ERRORS, OK, BAD_REQUEST, FORBIDDEN
from schemas import OnlineScoreRequest, ClientsInterestsRequest
from scoring import get_score, get_interests
from utils import is_online_score_request_valid, check_auth, get_auth_data


class MainHTTPHandler(BaseHTTPRequestHandler):
    """The request handler."""

    router = {"online_score": get_score, "clients_interests": get_interests}

    @staticmethod
    def get_request_id(headers: Message) -> str:
        """The method for creating the request ID."""

        return headers.get('HTTP_X_REQUEST_ID', uuid.uuid4().hex)

    def method_handler(self, request: dict, path: str, response: dict, code: int) -> tuple[dict, int]:
        """The method is a handler for specific requests."""

        if path == "online_score":
            try:
                request_data = OnlineScoreRequest(
                    first_name=request.get("arguments").get("first_name"),
                    last_name=request.get("arguments").get("last_name"),
                    email=request.get("arguments").get("email"),
                    phone=request.get("arguments").get("phone"),
                    birthday=request.get("arguments").get("birthday"),
                    gender=request.get("arguments").get("gender"),
                )
            except AttributeError as e:
                logging.exception("Attribute error: %s" % e)
                return response, INVALID_REQUEST
            except ValueError as e:
                logging.exception("Value error: %s" % e)
                return response, INVALID_REQUEST

            if not is_online_score_request_valid(request_data):
                logging.exception("Value error: there are no minimum required fields "
                                  "(phone-email or first name-last name or gender-birthday)")
                return response, INVALID_REQUEST

        elif path == "clients_interests":
            try:
                request_data = ClientsInterestsRequest(
                    client_ids=request.get("arguments").get("client_ids"),
                    date=request.get("arguments").get("date"),
                )
            except AttributeError as e:
                logging.exception("Attribute error: %s" % e)
                return response, INVALID_REQUEST
            except ValueError as e:
                logging.exception("Value error: %s" % e)
                return response, INVALID_REQUEST

        else:
            return response, NOT_FOUND

        try:
            response = self.router[path](request_data, request.get("login"))
        except Exception as e:
            logging.exception("Unexpected error: %s" % e)
            code = INTERNAL_ERROR

        return response, code

    def send_response_data(self, response: dict, code: int, context: dict) -> None:
        """The method that returns the result."""

        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if code not in ERRORS:
            r = {"response": response, "code": code}
        else:
            r = {"error": response or ERRORS.get(code, "Unknown Error"), "code": code}
        context.update(r)
        logging.info(context)
        self.wfile.write(json.dumps(r).encode('utf-8'))

    def do_POST(self) -> None:
        """Post API."""

        response, code = {}, OK
        context = {"request_id": self.get_request_id(self.headers)}
        request = None
        try:
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            request = json.loads(data_string)
        except:
            code = BAD_REQUEST

        path = self.path.strip("/")
        if not path or not request.get("login"):
            code = INVALID_REQUEST

        else:
            if request:
                if not (auth_data := get_auth_data(request)):
                    code = INVALID_REQUEST
                else:
                    if not check_auth(auth_data):
                        code = FORBIDDEN
                    else:
                        logging.info("%s: %s %s" % (self.path, data_string, context["request_id"]))

                        response, code = self.method_handler(request, path, response, code)

            elif request is not None:
                code = INVALID_REQUEST

        self.send_response_data(response, code, context)
        return


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-p", "--port", action="store", type=int, default=8080)
    parser.add_argument("-l", "--log", action="store", default=None)
    args = parser.parse_args()
    logging.basicConfig(filename=args.log, level=logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')
    server = HTTPServer(("localhost", args.port), MainHTTPHandler)
    logging.info("Starting server at %s" % args.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
