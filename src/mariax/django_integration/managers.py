from django.db import models
from django.db.models import F, Value
from django.db.models.expressions import Func

from ..vector import to_db_text


class VecFromText(Func):
    function = "VEC_FromText"
    arity = 1


class RawVecDistance(Func):
    template = "%(function)s(%(expressions)s)"

    def __init__(self, field_expr, vec_text_expr, metric="cosine", **extra):
        metric = (metric or "cosine").lower()
        if metric == "cosine":
            function = "VEC_DISTANCE_COSINE"
        elif metric in ("euclidean", "l2"):
            function = "VEC_DISTANCE_EUCLIDEAN"
        else:
            function = "VEC_DISTANCE"
        super().__init__(field_expr, vec_text_expr, function=function, **extra)


class VectorQuerySet(models.QuerySet):
    def _prep(self, vector):
        if isinstance(vector, str):
            # assume JSON text
            return vector
        return to_db_text(vector)


def similarity_search(self, vector, top_k=10, metric="cosine", embedding_field="embedding", prefilter=None):
    vec_text = self._prep(vector)
    vec_expr = VecFromText(Value(vec_text))
    field_expr = F(embedding_field)
    distance_expr = RawVecDistance(field_expr, vec_expr, metric=metric)
    qs = self
    if prefilter:
        qs = qs.filter(prefilter) if not isinstance(prefilter, dict) else qs.filter(**prefilter)
    ann = qs.annotate(vector_distance=distance_expr).order_by("vector_distance")
    return ann[:top_k]
