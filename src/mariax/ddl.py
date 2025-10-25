from typing import Optional, List


def vector_column_sql(column_name: str, dim: int, not_null: bool = True) -> str:
    if dim <= 0:
        raise ValueError("dim must be > 0")
    null_sql = "NOT NULL" if not_null else "NULL"
    return f"{column_name} VECTOR({dim}) {null_sql}"


def create_vector_index_sql(
    table: str, name: str, fields: List[str], distance: str = "cosine", m: Optional[int] = None
) -> str:
    if not fields:
        raise ValueError("fields must be non-empty")
    fields_sql = ", ".join(fields)
    m_sql = f" M={int(m)}" if m else ""
    return f"CREATE VECTOR INDEX {name} ON {table} ({fields_sql}) DISTANCE={distance}{m_sql};"


def drop_vector_index_sql(table: str, name: str) -> str:
    return f"DROP INDEX {name} ON {table};"
