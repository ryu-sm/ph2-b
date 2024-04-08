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

            # await crud.insert_c_access_log(
            #     db=DB(),
            #     account_id=payload["id"] if payload else None,
            #     ip=request.client.host,
            #     url=request.url._url,
            #     endpoint=utils.parse_endpoint(request.url.path, request.path_params),
            #     method=request.method,
            #     params={
            #         "path": dict(request.path_params) if request.path_params else None,
            #         "query": dict(request.query_params) if request.query_params else None,
            #         "body": json.loads(request_body) if request_body else None,
            #     },
            #     status_code=response.status_code,
            #     response_body=json.loads(response.body.decode("utf-8")),
            # )
            return response

        return custom_route_handler


class AuthException(Exception):
    def __init__(self):
        Exception.__init__(self)
        self.name = "JWT token verify exception."
