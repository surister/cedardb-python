import pytest

from cedardb.client import _create_insert_query


def test_insert_query():
    table_name = "mytbl"
    query = _create_insert_query(table_name=table_name, row_count=2)
    assert query == 'insert into "mytbl" values (%s,%s)'

    query = _create_insert_query(
        table_name=table_name, row_count=2, columns=["col1", "col2"]
    )
    assert query == 'insert into "mytbl" (col1,col2) values (%s,%s)'

    query = _create_insert_query(table_name=table_name, row_count=2, placeholder="?")
    assert query == 'insert into "mytbl" values (?,?)'

    with pytest.raises(AttributeError):
        _create_insert_query(None, row_count=1)
        _create_insert_query("some", row_count=None)
