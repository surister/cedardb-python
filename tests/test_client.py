from unittest import mock
import pytest

import psycopg

from cedardb.client import Client
from tests.conftest import psycopg_mocked_with

client = Client(
    host="localhost", dbname="testdb", user="admin", password="secret", port="1234"
)


def test_client_uri():
    expected_uri = (
        "host=localhost" " port=1234" " dbname=testdb" " user=admin" " password=secret"
    )

    assert client.conn_string == expected_uri


@psycopg_mocked_with(rows=[(1, None), (2, 1)], columns=["column1", "column2"])
def test_client_select_ok(psycopg_mock):
    with mock.patch("psycopg.connect", return_value=psycopg_mock):
        r = client.query("select * from table")

        assert r.ok is True
        assert r.rows
        assert r.columns == ["column1", "column2"]
        assert r.rows == [(1, None), (2, 1)]
        assert r.row_count == 2
        assert r.exception is None
        assert r.error_message is None


@psycopg_mocked_with(raise_error=psycopg.errors.SyntaxError("some_error"))
def test_client_select_ko(psycopg_mock):
    with mock.patch("psycopg.connect", return_value=psycopg_mock):
        r = client.query("selec * from table")

        assert r.ok is False
        assert r.rows == []
        assert r.columns == []
        assert r.row_count == -1

        assert isinstance(r.exception, psycopg.errors.SyntaxError)
        assert r.error_message == "some_error"


@psycopg_mocked_with(raise_error=psycopg.errors.SyntaxError("some_error"))
def test_client_select_ko(psycopg_mock):
    with mock.patch("psycopg.connect", return_value=psycopg_mock):
        with pytest.raises(psycopg.errors.SyntaxError):
            client.query("selec * from table", raise_exception=True)
