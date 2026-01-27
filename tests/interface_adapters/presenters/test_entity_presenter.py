import pytest

from dojocommons.interface_adapters.dtos.response import Response
from dojocommons.interface_adapters.http.cors_helper import CORSHelper
from dojocommons.interface_adapters.presenters.base import EntityPresenter


@pytest.mark.parametrize(
    "code, body, expected",
    [
        (
            None,
            {"key": "value"},
            Response(
                status_code=200,
                headers=CORSHelper.get_cors_headers(),
                body={"data": {"key": "value"}},
            ),
        ),
        (
            None,
            [{"key1": "value1", "key2": "value2"}],
            Response(
                status_code=200,
                headers=CORSHelper.get_cors_headers(),
                body={"data": [{"key1": "value1", "key2": "value2"}]},
            ),
        ),
        (
            None,
            None,
            Response(
                status_code=200,
                headers=CORSHelper.get_cors_headers(),
                body=None,
            ),
        ),
        (
            204,
            None,
            Response(
                status_code=204,
                headers=CORSHelper.get_cors_headers(),
                body=None,
            ),
        ),
    ],
)
def test_present(code, body, expected):
    presenter = EntityPresenter()

    if code is None:
        response: Response = presenter.present(body)
    else:
        response: Response = presenter.present(body, code)

    assert response == expected


def test_present_error():
    presenter = EntityPresenter()

    response: Response = presenter.present_error(500, "internal server error")

    expected = Response(
        status_code=500,
        headers=CORSHelper.get_cors_headers(),
        body={"error": {"message": "internal server error", "code": 500}},
    )

    assert response == expected
