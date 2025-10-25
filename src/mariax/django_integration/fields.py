from django.db import models

from mariax.vector import validate_vector, to_db_text


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

    def from_db_value(self, value, expression, connection):
        # Keep raw value (driver dependent); callers may decode via mariax.vector.from_db_value
        return value

    def get_prep_value(self, value):
        if value in (None, ""):
            return None
        vec = validate_vector(value, self.dim)
        # Return JSON text and rely on get_placeholder to wrap with VEC_FromText(%s)
        return to_db_text(vec)

    def get_placeholder(self, value, compiler, connection):
        # Django ORM calls this internally when rendering SQL for INSERT/UPDATE.
        # Returning VEC_FromText(%s) ensures our JSON text param is converted to
        # a native MariaDB VECTOR on the server side.
        return "VEC_FromText(%s)"
