from cedardb.client import Client


def test_client_uri():
    client = Client(
        host="localhost", dbname="testdb", user="admin", password="secret", port="1234"
    )

    expected_uri = (
        "host=localhost" " port=1234" " dbname=testdb" " user=admin" " password=secret"
    )

    assert client.conn_string == expected_uri
