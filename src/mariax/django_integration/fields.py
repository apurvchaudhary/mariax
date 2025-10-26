"""
vector field module
"""
from ast import literal_eval

import numpy as np
from django.db import models

from mariax.vector import validate_vector, to_db_text, from_db_value as vec_from_db_value


class VectorField(models.Field):
    """
    Django Field representing MariaDB VECTOR(dim).
    Stores vectors as MariaDB VECTOR type. On save, values are validated and
    serialized to JSON text, which the placeholder converts via VEC_FromText(%s).
    """

    description = "MariaDB VECTOR field"

    def __init__(self, dim: int, *args, **kwargs):
        if not isinstance(dim, int) or dim <= 0:
            raise ValueError("dim must be positive int")
        self.dim = dim
        super().__init__(*args, **kwargs)

    def db_type(self, connection):
        """
        Generates and returns the database column type as a string, specifically
        for creating a vector column with a defined dimensional size.

        :param connection: The database connection object.
        :type connection: Any
        :return: The string representation of the database column type for a dimensional vector.
        :rtype: Str
        """
        return f"VECTOR({self.dim})"

    def deconstruct(self):
        """
        Deconstructs the instance into a tuple containing the name, path, args, and kwargs.

        The method modifies the keyword arguments (`kwargs`) to include the `dim`
        attribute of the instance.

        :return: A tuple containing the name, path, arguments, and modified keyword arguments of the instance.
        :rtype: Tuple
        """
        name, path, args, kwargs = super().deconstruct()
        kwargs["dim"] = self.dim
        return name, path, args, kwargs

    @staticmethod
    def from_db_value(value, *args, **kwargs):
        """
        Converts a database value into a Python object. This method handles various
        data formats that might be stored in the database, such as raw binary data,
        bytes/memory, or JSON/text. It returns the corresponding Python
        representation.

        :param value: The value retrieved from the database that needs to be converted.
        :type value: Any
        :param args: Additional positional arguments that might be passed to the method for processing.
        :type args: Tuple
        :param kwargs: Additional keyword arguments that might be passed to the method for processing.
        :type kwargs: Dict
        :return: The converted Python object
        :rtype: List, None
        """
        if value in (None, ""):
            return None
        # If it’s bytes or MariaDB returns a memoryview
        if isinstance(value, (bytes, memoryview, bytearray)):
            # Convert raw binary VECTOR → float32 array → list
            return np.frombuffer(bytes(value), dtype=np.float32).tolist()
        # If stored as JSON/text
        return vec_from_db_value(value)

    def get_prep_value(self, value):
        """
        Transforms and prepares the input value for storage in the database. The method
        ensures the input value is validated, converted to a vector, and properly
        serialized for database storage.

        :param value: The input value to be prepared.
        :type value: Any
        :return: The processed and serialized vector as a JSON-compatible string or None
        :rtype: str or None
        :raises ValueError: If the input value is invalid or does not meet the dimension requirements.
        """
        if value in (None, ""):
            return None
        if isinstance(value, str):
            try:
                value = literal_eval(value)
            except (ValueError, SyntaxError):
                pass
        if isinstance(value, (bytes, bytearray, memoryview)):
            arr = np.frombuffer(value, dtype=np.float32)
            value = arr.tolist()
        # Validate dimension and types, then serialize
        vec = validate_vector(value, self.dim)
        # Return JSON text and rely on get_placeholder to wrap with VEC_FromText(%s)
        return to_db_text(vec)

    @staticmethod
    def get_placeholder(*args, **kwargs):
        """
        Returns a placeholder string to be used in SQL rendering for INSERT/UPDATE
        operations. This is a static method called internally by the Django ORM,
        ensuring that a JSON text parameter is converted to a native MariaDB VECTOR
        on the server side.

        :param args: Positional arguments passed to the method
        :param kwargs: Keyword arguments passed to the method
        :return: A string representing the placeholder "VEC_FromText(%s)"
        :rtype: str
        """
        # Django ORM calls this internally when rendering SQL for INSERT/UPDATE.
        # Returning VEC_FromText(%s) ensures our JSON text param is converted to
        # a native MariaDB VECTOR on the server side.
        return "VEC_FromText(%s)"
