"""
queryset manager module
"""
from django.db import models
from django.db.models import F, Value
from django.db.models import FloatField
from django.db.models.expressions import Func

from mariax.vector import to_db_text


class VecFromText(Func):
    """
    Represents a vector creation function from text input.

    This class is used to encapsulate a function that creates a vector
    from a textual representation. It is designed to work as a single-arity
    function and has an optional output field that specifies where the result
    should be stored or represented. Its main utility would typically be in
    contexts requiring vectorization of input text.

    :ivar function: Name of the function that generates the vector.
    :type function: Str
    :ivar arity: Specifies the number of arguments the function can accept.
    :type arity: Int
    :ivar output_field: Optional field to store or represent the output of the operation. Defaults to None.
    :type output_field: Any
    """
    function = "VEC_FromText"
    arity = 1
    output_field = None


class RawVecDistance(Func):
    """
    Represents a specialized function for calculating vector distances in database queries.

    The class allows users to compute vector distances between a given field and a vector text
    expression using specified distance metrics. It supports various metrics such as cosine
    similarity and Euclidean distance. The purpose of this class is to encapsulate the logic
    required for applying vector distance computations within database query expressions.

    :ivar template: SQL function template used to represent the calculation function in query expressions.
    :type template: Str
    """
    template = "%(function)s(%(expressions)s)"

    def __init__(self, field_expr, vec_text_expr, metric="cosine", **extra):
        metric = (metric or "cosine").lower()
        if metric == "cosine":
            function = "VEC_DISTANCE_COSINE"
        elif metric in ("euclidean", "l2"):
            function = "VEC_DISTANCE_EUCLIDEAN"
        else:
            function = "VEC_DISTANCE"
        extra.setdefault("output_field", FloatField())
        super().__init__(field_expr, vec_text_expr, function=function, **extra)


class VectorQuerySet(models.QuerySet):
    """
    Custom QuerySet for performing vector similarity operations on database records.

    This class extends the Django QuerySet to include functionalities for similarity
    searching and finding nearest neighbors based on vector representations. These
    operations are often used in machine learning and information retrieval tasks
    involving embeddings.
    """
    @staticmethod
    def _prep(vector):
        """
        Prepares the input vector by converting it to a database-compliant text
        format if it is not already a string.

        :param vector: The input vector that can either be of type string or another
            type which needs conversion to a database-compliant string.
        :type vector: Any
        :return: The prepared vector as a string, suitable for database storage.
        :rtype: Str
        """
        if isinstance(vector, str):
            # assume JSON text
            return vector
        return to_db_text(vector)

    def __common(self, vector, top_k, metric, embedding_field, prefilter, order_by):
        """
        Performs a similarity search by finding the nearest neighbors to a provided vector.
        This function computes distances between the provided vector and existing embeddings
        stored in the dataset, optionally filters the results based on a pre-defined condition,
        and orders the output according to the specified order by field.
        """
        vec_expr = VecFromText(Value(self._prep(vector)))
        field_expr = F(embedding_field)
        distance_expr = RawVecDistance(field_expr, vec_expr, metric=metric)
        qs = self
        if prefilter:
            qs = qs.filter(prefilter) if not isinstance(prefilter, dict) else qs.filter(**prefilter)
        ann = qs.annotate(vector_distance=distance_expr).order_by(order_by)
        return ann[:top_k]

    def similarity_search(self, vector, top_k=10, metric="cosine", embedding_field="embedding", prefilter=None):
        """
        Perform similarity search using a specified metric on the embedding space.

        This method calculates the similarity between a given vector and items in the
        embedding space. It allows for searching based on the specified metric and
        supports optional pre-filtering capabilities for narrowing down the candidates
        before similarity computation.

        :param vector: The input vector for which the similarity search is performed.
        :param top_k: Number of most similar results to be retrieved. Defaults to 10.
        :param metric: Metric used for similarity calculation, such as "cosine".
            Defaults to "cosine".
        :param embedding_field: The field in the dataset that contains the embedding
            vector. Defaults to "embedding".
        :param prefilter: Optional prefilter logic to refine candidate selection prior
            to similarity calculation. Defaults to None.
        :return: The top-k most similar items are determined based on the provided metric.
        """
        return self.__common(vector, top_k, metric, embedding_field, prefilter, "vector_distance")

    def nearest_neighbors(self, vector, top_k=10, metric="cosine", embedding_field="embedding", prefilter=None):
        """
        Finds the nearest neighbors to the provided vector based on the specified metric
        from a given embedding field. Additionally, allows applying a prefilter to narrow
        down the search. The method computes distances or similarities and retrieves the
        top-k closest neighbors.

        :param vector: The input vector for which the nearest neighbors are to be found
        :param top_k: The number of top neighbors to retrieve (default is 10)
        :param metric: The metric used to calculate similarity or distance (default is "cosine")
        :param embedding_field: The field containing the embeddings to compare against (default is "embedding")
        :param prefilter: An optional prefilter function to apply before searching for neighbors
        :return: List of nearest neighbors and their respective distances/similarities
        """
        return self.__common(vector, top_k, metric, embedding_field, prefilter, "neighbor_distance")
