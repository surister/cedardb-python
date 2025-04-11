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
    def uri(self):
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
