from typing import Optional, List


def vector_column_sql(column_name: str, dim: int, not_null: bool = True) -> str:
    """
    Generate a SQL column definition for a vector data type.

    This function creates a SQL-compatible definition for a vector column, where
    the dimensionality of the vector and nullability can be specified.

    :param column_name: The name of the column in the database.
    :param dim: The dimensionality of the vector must be greater than 0.
    :param not_null: Whether the column should be marked as NOT NULL. Defaults to True.
    :return: The SQL string defining the vector column.
    """
    if dim <= 0:
        raise ValueError("dim must be > 0")
    null_sql = "NOT NULL" if not_null else "NULL"
    return f"{column_name} VECTOR({dim}) {null_sql}"


def create_vector_index_sql(
    table: str, name: str, fields: List[str], distance: str = "cosine", m: Optional[int] = None
) -> str:
    """
    Generates SQL statement to create a vector index on a specified table with specified fields.

    This function constructs a SQL string for creating a vector index with specific
    fields, distance metric, and an optional `m` parameter. The `m` parameter allows
    further customization of the index.

    :param table: The name of the table on which the vector index will be created.
    :param name: The name of the vector index to be created.
    :param fields: A list of field names to be included in the vector index.
    :param distance: The distance metric to be used in the vector index (default is "cosine").
    :param m: Optional parameter to specify the `M` value for the index configuration.
    :return: The SQL string for creating the vector index.
    :rtype: Str
    :raises ValueError: If the `fields` parameter is empty.
    """
    if not fields:
        raise ValueError("fields must be non-empty")
    fields_sql = ", ".join(fields)
    m_sql = f" M={int(m)}" if m else ""
    return f"CREATE VECTOR INDEX {name} ON {table} ({fields_sql}) DISTANCE={distance}{m_sql};"


def drop_vector_index_sql(table: str, name: str) -> str:
    """
    Generate a SQL query to drop an index from a table.

    This function creates and returns a SQL command string that can be used
    to drop an index, specified by its name, from the given database table.

    :param table: The name of the database table from which the index is to be dropped.
    :type table: Str.
    :param name: The name of the index to drop.
    :type name: Str
    :return: A SQL query string to drop the specified index.
    :rtype: Str
    """
    return f"DROP INDEX {name} ON {table};"
