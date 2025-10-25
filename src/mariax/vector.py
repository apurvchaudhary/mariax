"""Utility helpers for working with MariaDB VECTOR values.

Public API:
- validate_vector: ensure an iterable of numbers with optional fixed dimension
- to_db_text: serialize a vector to JSON text accepted by VEC_FromText(%s)
- from_db_value: deserialize database-returned value into a list[float]
"""

import json
from typing import Iterable, List, Optional, Sequence, Union

__all__ = [
    "validate_vector",
    "to_db_text",
    "from_db_value",
]


def validate_vector(vec: Iterable[float], dim: Optional[int] = None) -> List[float]:
    """Validate and normalize a vector-like input to a list of floats.

    - vec: any iterable with numeric items
    - dim: if provided, enforces exact length
    """
    if vec is None:
        raise ValueError("vector must not be None")
    try:
        arr = [float(x) for x in vec]
    except (TypeError, ValueError) as e:
        raise ValueError("vector must be an iterable of numbers") from e
    if dim is not None and len(arr) != dim:
        raise ValueError(f"expected vector dim={dim}, got {len(arr)}")
    return arr


def to_db_text(vec: Iterable[float], dim: Optional[int] = None) -> str:
    """Serialize a vector to JSON text suitable for VEC_FromText(%s)."""
    arr = validate_vector(vec, dim)
    return json.dumps(arr, separators=(",", ":"))


DbScalar = Union[str, bytes, float, int]


def from_db_value(value: Union[DbScalar, Sequence[float], None]) -> Optional[List[float]]:
    """Convert various database-returned representations into list[float].

    Accepts:
    - None -> None
    - list/tuple of numbers -> list[float]
    - JSON text or bytes (e.g., "[0.1, 0.2]") -> list[float]
    - Fallback: comma-separated text without brackets -> list[float]
    - Scalar number -> [float(value)]
    """
    if value is None:
        return None

    if isinstance(value, (list, tuple)):
        return [float(x) for x in value]

    if isinstance(value, (bytes, str)):
        s = value.decode() if isinstance(value, bytes) else value
        s = s.strip()
        if not s:
            return []
        try:
            loaded = json.loads(s)
            return [float(x) for x in loaded]
        except (json.JSONDecodeError, TypeError, ValueError):
            # Fallback: tolerate bracketed or plain comma-separated forms
            s2 = s.strip("[]() {}")
            if not s2:
                return []
            return [float(x) for x in (part.strip() for part in s2.split(",")) if x]

    # Fallback for scalar numeric types
    return [float(value)]
