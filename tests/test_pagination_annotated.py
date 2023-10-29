"""Test case to ensure that forward references are resolved correctly in functions decorated with `@paginate`.

Specifically, this is tested via a case where `__future__.annotations` has been imported and an API endpoint
has been defined alongside a `Schema` that defines its query parameters.
"""

from __future__ import annotations

from typing import Any, List

import pytest
from django.http import HttpRequest

from ninja import NinjaAPI, Query, Schema
from ninja.pagination import paginate
from ninja.testing import TestClient
from ninja.types import DictStrAny

api = NinjaAPI()

ITEMS = list(range(100))


class Filters(Schema):
    example_filter: str = ""


@api.get("/items_1", response=List[int])
@paginate
def items_1(request: HttpRequest, filters: Filters = Query(...)) -> List[int]:
    return ITEMS


client = TestClient(api)


def test_paginated_endpoint_with_annotations() -> None:
    response = client.get("/items_1?limit=10").json()

    assert "items" in response, response.keys()
    assert "count" in response, response.keys()
    assert response["items"] == ITEMS[:10]
    assert response["count"] == 100

    schema = api.get_openapi_schema()["paths"]["/api/items_1"]["get"]

    assert "parameters" in schema, list(schema.keys())
    assert schema["parameters"] == [
        {
            "in": "query",
            "name": "example_filter",
            "schema": {
                "default": "",
                "title": "Example Filter",
                "type": "string",
            },
            "required": False,
        },
        {
            "in": "query",
            "name": "limit",
            "schema": {
                "title": "Limit",
                "default": 100,
                "minimum": 1,
                "type": "integer",
            },
            "required": False,
        },
        {
            "in": "query",
            "name": "offset",
            "schema": {
                "title": "Offset",
                "default": 0,
                "minimum": 0,
                "type": "integer",
            },
            "required": False,
        },
    ]
