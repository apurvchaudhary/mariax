from typing import Any, Iterable, Tuple

from mariax.client import DBClient
from mariax.vector import to_db_text


def _metric_to_func(metric: str) -> str:
    """Map a user metric string to the corresponding MariaDB function name."""
    m = (metric or "cosine").strip().lower()
    if m == "cosine":
        return "VEC_DISTANCE_COSINE"
    if m in ("euclidean", "l2"):
        return "VEC_DISTANCE_EUCLIDEAN"
    return "VEC_DISTANCE"


def similarity_search(
    client: DBClient,
    table: str,
    embedding_field: str,
    vector: Iterable[float],
    top_k: int = 10,
    metric: str = "cosine",
    where_sql: str = "",
    where_params: Tuple[Any, ...] = (),
):
    """
    Perform a similarity search on a database table containing vector embeddings.
    This function queries the specified database table to find the closest vectors
    to the provided query vector, according to the specified similarity metric.
    The results are ordered by similarity and limited to the specified number
    of top results.
    """
    func = _metric_to_func(metric)
    vec_text = to_db_text(vector)
    sql = f"""
        SELECT *,
               {func}({embedding_field}, VEC_FromText(%s)) AS vector_distance
        FROM {table}
        WHERE 1=1 {where_sql}
        ORDER BY vector_distance ASC
        LIMIT %s;
    """
    params = (vec_text, *where_params, top_k)
    return client.fetchall(sql, params)


def nearest_neighbors(
    client: DBClient,
    table: str,
    embedding_field: str,
    vector: Iterable[float],
    top_k: int = 10,
    metric: str = "cosine",
):
    """
    Find the nearest neighbors based on a given embedding vector using a specified
    distance metric. This method calculates distances between a target vector and
    vectors stored in a database table to identify the closest matches.
    The query supports multiple distance metrics including cosine, Euclidean, or
    default unspecified metric. Results are sorted in ascending order of distance.
    """
    func = _metric_to_func(metric)
    vec_text = to_db_text(vector)

    sql = f"""
        SELECT *,
               {func}({embedding_field}, VEC_FromText(%s)) AS neighbor_distance
        FROM {table}
        ORDER BY neighbor_distance
        LIMIT %s;
    """
    params = (vec_text, top_k)
    return client.fetchall(sql, params)
