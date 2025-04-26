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

        r = client.query("selec * from table", raise_exception=False)
        assert r.error_message == "some_error"
        assert isinstance(r.exception, psycopg.errors.Error)


@psycopg_mocked_with(rows=[], columns=[], rowcount=2)
def test_client_insert_many(psycopg_mock):
    with mock.patch("psycopg.connect", return_value=psycopg_mock):
        rows = ((1, "somedata"), (2, "somedata2"))
        r = client.insert_many("mytbl", rows)
        assert r.row_count == 2
        assert r.ok is True
        assert not r.rows
        assert not r.columns
        assert r.original_statement_type == "INSERT PIPELINE"


@psycopg_mocked_with(
    raise_error=psycopg.errors.SyntaxError("some_error"),
    side_effect_method="executemany",
)
def test_client_insert_many_ko(psycopg_mock):
    with mock.patch("psycopg.connect", return_value=psycopg_mock):
        rows = ((1, "somedata"), (2, "somedata2"))
        with pytest.raises(psycopg.errors.SyntaxError):
            client.insert_many("mytbl", rows, raise_exception=True)

        r = client.insert_many("mytbl", rows, raise_exception=False)

        assert r.ok is False
        assert r.error_message == "some_error"
        assert isinstance(r.exception, psycopg.errors.Error)
