import psycopg

from cedardb.response import QueryResponse


class Client:
    def __init__(
        self, host: str, dbname: str, user: str, password: str, port: str = "5432"
    ):
        self.host = host
        self.dbname = dbname
        self.user = user
        self.password = password
        self.port = port

    @property
    def conn_string(self):
        """Returns a PostgreSQL connection string in key-values.

        Examples:
            >>> Client(host="localhost", dbname="testdb", user="admin", password="secret", port="1234")
            "host=localhost port=1234 dbname=testdb user=admin password=secret"
        """
        return (
            f"host={self.host}"
            f" port={self.port}"
            f" dbname={self.dbname}"
            f" user={self.user}"
            f" password={self.password}"
        )

    def get_conn(self):
        return psycopg.connect(self.conn_string)

    def query(self, statement: str, raise_exception: bool = False) -> QueryResponse:
        with self.get_conn() as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute(statement)
                    response = QueryResponse.from_cur(cur)
                except psycopg.errors.Error as e:
                    response = QueryResponse.from_error(e, cur.statusmessage)

                    if raise_exception:
                        raise e

                return response
