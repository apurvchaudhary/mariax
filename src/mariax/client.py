import contextlib
from typing import Any, Iterable, Optional, Tuple, List


class DBClient:
    """
    DBClient provides methods to interact with a database connection.

    This class encapsulates common database operations such as executing SQL
    statements, fetching all results, and fetching a single result. It provides
    a straightforward interface for interacting with a database and ensures
    safe management of database resources during these operations.

    :ivar conn: The database connection object used for executing queries.
    :type conn: Any
    """

    def __init__(self, connection):
        self.conn = connection

    def __commit(self):
        """
        Commits the current transaction to the database.

        This method is used to apply all changes made in the
        current transaction to the database. It ensures data
        consistency and makes modifications permanent.

        :return: None
        """
        self.conn.commit()

    def execute(self, sql: str, params: Optional[Iterable[Any]] = None) -> int:
        """
        Executes a given SQL statement using the provided parameters and returns the number
        of rows affected. This method ensures the execution is performed within a context
        that properly closes the cursor after the operation. Additionally, changes to the
        database are committed automatically after the SQL execution.

        :param sql: The SQL statement to execute as a string.
        :param params: Optional iterable of parameters to substitute in the SQL statement.
        :return: The number of rows affected by the SQL execution.
        :rtype: Int
        """
        with contextlib.closing(self.conn.cursor()) as cur:
            cur.execute(sql, params or ())
            self.__commit()
            return cur.rowcount

    def fetchall(self, sql: str, params: Optional[Iterable[Any]] = None) -> List[Tuple]:
        """
        Executes the provided SQL query with optional parameters and retrieves all rows
        from the result set.

        :param sql: The SQL query to execute.
        :param params: A collection of parameters to safely inject into the query. Defaults to None.
        :return: A list of tuples where each tuple represents a row returned by the query.
        """
        with contextlib.closing(self.conn.cursor()) as cur:
            cur.execute(sql, params or ())
            return cur.fetchall()

    def fetchone(self, sql: str, params: Optional[Iterable[Any]] = None):
        """
        Executes a SQL query expected to return a single row of results and retrieves this row.

        This method interacts with the connected database using a specified SQL query and parameters to
        fetch a single row of data. By default, the query will be executed with an empty parameter set
        if none is provided. The caller can then use the returned data for further processing.

        :param sql: The SQL query string to be executed.
        :type sql: Str
        :param params: An optional iterable containing the parameters to be used in the SQL query.
                       If none is provided, an empty set of parameters is used.
        :type params: Optional[Iterable[Any]]
        :return: A single row resulting from the SQL query execution or ``None`` if no data was found.
        :rtype: Any
        """
        with contextlib.closing(self.conn.cursor()) as cur:
            cur.execute(sql, params or ())
            return cur.fetchone()
