import typing
from typing import Any, Generator

from unittest import mock
from unittest.mock import MagicMock

import pytest


def col_with(**kwargs):
    """Returns an object that sets all the received key=value as attributes.

    Used to easily mock `cursor.description`.

    Example:
        >>> col = col_with(name='myname', some_other_key='other_value')
        >>> col.name
        'myname'
        >>> col.some_other_key
        'other_value'
    """
    o = type("column", (), {})
    for k, v in kwargs.items():
        setattr(o, k, v)
    return o


@pytest.fixture()
def psycopg_mock(request) -> Generator[MagicMock, Any, None]:
    """This mocks psycopg.connect chain, including:

    psycopg.connect
    psycopg.connect.cursor
    psycopg.connect.cursor.rowcount
    psycopg.connect.cursor.fetchall
    psycopg.connect.cursor.description

    It receives a parameter (request.param) to automatically set expected rows and columns.
     It's best used with the decorator `psycopg_mocked_with`, as it sets a named parameter API that is
    less prone to mistakes, since we will need in the future to further customize the Mock.

    Example:
    >>>@psycopg_mocked_with(rows=[(1, None), (2, 3)], columns=['column1', 'column2'])
    >>>def test_client(psycopg_mock):
    >>>    with mock.patch('psycopg.connect', return_value=psycopg_mock):
    >>>        client = Client(
    >>>        host="localhost",
    >>>        dbname="testdb",
    >>>        user="admin",
    >>>        password="secret",
    >>>        port="1234"
    >>>    )
    >>>    r = client.query('select * from table')
    >>>    print(r.as_table())
    +---------+---------+
    | column1 | column2 |
    +---------+---------+
    | 1       | None    |
    | 2       | 3       |
    +---------+---------+

    """
    rows, columns, error = request.param

    if not rows:
        rows = [list()]

    mock_connect = MagicMock()

    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_cursor.fetchall.return_value = rows

    mock_cursor.rowcount = len(rows)
    mock_cursor.statusmessage = f"mocked"

    if error:
        mock_cursor.execute.side_effect = error

    if columns:
        mock_cursor.description = [col_with(name=col) for col in columns]

    if not columns and rows:
        # If we don't specify column names, we make them up.
        mock_cursor.description = [
            col_with(name=f"column_{_}") for _ in range(len(rows[0]))
        ]

    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    # this is what psycopg.connect() returns
    mock_connect.__enter__.return_value = mock_conn

    yield mock_connect


def psycopg_mocked_with(
    *, rows: list = None, columns: list = None, raise_error=None
) -> typing.Callable:
    def decorator(func):
        return pytest.mark.parametrize(
            "psycopg_mock", [(rows, columns, raise_error)], indirect=True
        )(func)

    return decorator
