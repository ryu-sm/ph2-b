import json
from typing import Callable
from fastapi import Request
from fastapi import Response
from fastapi.routing import APIRoute

from core.database import DB
import crud
import utils


# TODO: delete
class LoggingContextRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            response: Response = await original_route_handler(request)
            payload = utils.only_parse_payload(request.headers.get("authorization"))
            request_body = await request.body()

            return response

        return custom_route_handler


class AuthException(Exception):
    def __init__(self):
        Exception.__init__(self)
        self.name = "JWT token verify exception."
