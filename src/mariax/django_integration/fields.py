from django.db import models

from ..vector import to_db_text, validate_vector


class VectorField(models.Field):
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
        # leave raw value (driver dependent); user can call mariax.vector.from_db_value
        return value

    def get_prep_value(self, value):
        if value is None:
            return None
        vec = validate_vector(value, self.dim)
        return to_db_text(vec)
