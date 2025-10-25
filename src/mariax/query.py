from typing import Iterable, Tuple

from .client import DBClient
from .vector import to_db_text


def similarity_search(
    client: DBClient,
    table: str,
    embedding_field: str,
    vector: Iterable[float],
    top_k: int = 10,
    metric: str = "cosine",
    where_sql: str = "",
    where_params: Tuple = (),
):
    metric = metric.lower()
    if metric == "cosine":
        func = "VEC_DISTANCE_COSINE"
    elif metric in ("euclidean", "l2"):
        func = "VEC_DISTANCE_EUCLIDEAN"
    else:
        func = "VEC_DISTANCE"
    vec_text = to_db_text(vector)
    sql = f"SELECT *, {func}({embedding_field}, VEC_FromText(%s)) AS vector_distance FROM {table} WHERE 1=1 {where_sql} ORDER BY vector_distance ASC LIMIT %s;"
    params = (vec_text, *where_params, top_k)
    return client.fetchall(sql, params)
