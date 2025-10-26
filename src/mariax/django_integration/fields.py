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
        return f"VECTOR({self.dim})"

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs["dim"] = self.dim
        return name, path, args, kwargs

    @staticmethod
    def from_db_value(value, *args, **kwargs):
        if value in (None, ""):
            return None
        # If it’s bytes or MariaDB returns a memoryview
        if isinstance(value, (bytes, memoryview, bytearray)):
            # Convert raw binary VECTOR → float32 array → list
            return np.frombuffer(bytes(value), dtype=np.float32).tolist()
        # If stored as JSON/text
        return vec_from_db_value(value)

    def get_prep_value(self, value):
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
        # Django ORM calls this internally when rendering SQL for INSERT/UPDATE.
        # Returning VEC_FromText(%s) ensures our JSON text param is converted to
        # a native MariaDB VECTOR on the server side.
        return "VEC_FromText(%s)"
