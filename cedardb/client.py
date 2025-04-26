import psycopg

from cedardb.response import QueryResponse


def _create_insert_query(
    table_name: str,
    row_count: int,
    columns: list[str] | None = None,
    placeholder: str = "%s",
) -> str:
    """Creates an insert query with value placeholders.

    Args:
        table_name: The name of the table.
        row_count: How many values will be inserted, for placeholder generation.

    Returns:
        The insert query.

    Examples:
        >>> _create_insert_query("tbl", 4, ['col1', 'col2'])
        'insert into "tbl" ("col1", "col2") values (%s,%s,%s,%s)'
        >>> _create_insert_query("tbl", 3)
        'insert into "tbl" values (%s, %s, %s)'

    """
    if not table_name or not row_count:
        raise AttributeError(
            "In order to generate an insert query we need the table name and row_count to be"
            f" valid, but table_name={table_name!r} and row_count={row_count!r} was passed"
        )
    placeholders = f"{placeholder}," * row_count
    columns = " " + "(" + ",".join(columns) + ")" + " " if columns else " "
    if row_count > 0:
        placeholders = placeholders[:-1]

    return f'insert into "{table_name}"{columns}values ({placeholders})'


class Client:
    """Represents a client connecting to CedarDB instance.

    Examples:
        >>> from cedardb import Client
        >>> client = Client('localhost', dbname='postgres', user='postgres', password='postgres')

    """

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

    def get_conn(self) -> psycopg.connection.Connection:
        """Returns a psycopg connection"""
        return psycopg.connect(self.conn_string)

    def query(
        self, statement: str, raise_exception: bool = False, factory=None
    ) -> QueryResponse:
        """
        Runs a sql `statement` to the connection.

        Args:
            statement:
            raise_exception:
            factory:

        Returns:

        """
        with self.get_conn() as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute(statement)
                    response = QueryResponse.from_cur(cur, factory=factory)
                except psycopg.errors.Error as e:
                    response = QueryResponse.from_error(e, cur.statusmessage)

                    if raise_exception:
                        raise e

                return response

    def insert_many(
        self, table_name: str, rows, raise_exception: bool = False
    ) -> QueryResponse:
        """
        Leverages pipelining to bulk insert.

        See https://cedardb.com/docs/clients/python/#bulk-loading

        Examples:
            >>> rows = [ (1, 'data'), (2, 'data2')]
            >>> client.insert_many('table_name', rows)
        """
        statements = _create_insert_query(table_name, len(rows[0]))

        with self.get_conn() as conn:
            with conn.cursor() as cur:
                try:
                    cur.executemany(statements, rows)
                    response = QueryResponse.from_cur(
                        cur,
                        original_statement_type="INSERT PIPELINE",
                        result_expected=False,
                    )
                except psycopg.errors.Error as e:
                    response = QueryResponse.from_error(e, cur.statusmessage)

                    if raise_exception:
                        raise e

                return response
