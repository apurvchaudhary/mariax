"""
Utility helpers for working with MariaDB VECTOR values.

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
    """
    Validates if the input vector is an iterable of numbers and optionally checks its dimension.

    This function ensures that the input vector is not None and is an iterable containing numbers.
    If a dimension is specified, it checks if the length of the vector matches the given dimension.

    :param vec: The input vector to be validated. Must be an iterable of numbers.
    :type vec: Iterable[float]
    :param dim: The expected dimension of the vector. If provided, the function checks
                whether the length of the input vector matches this value.
    :type dim: Optional[int]
    :return: A list of float values representing a validated vector. The function converts
             the elements of the input iterable to floats.
    :rtype: List[float]
    :raises ValueError: If the input vector is None, contains non-numeric elements, or does
                        not match the specified dimension when `dim` is provided.
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
    """
    Converts a vector into a JSON string representation. This function validates the input
    vector against the optional dimension if provided before converting the validated vector
    to a compact JSON string format without unnecessary spaces.

    :param vec: The vector to be validated and converted. Must be an iterable of floats.
    :param dim: Optional. If provided, specifies the expected dimension of the vector.
    :return: A JSON string representing the validated vector.
    """
    arr = validate_vector(vec, dim)
    return json.dumps(arr, separators=(",", ":"))


DbScalar = Union[str, bytes, float, int]


def from_db_value(value: Union[DbScalar, Sequence[float], None]) -> Optional[List[float]]:
    """
    Converts a database value into a list of floats. Handles different input types including
    None, list, tuple, bytes, string, and scalar numeric values. For string-based inputs,
    it attempts to parse JSON if the string appears to be JSON-encoded. If parsing fails,
    it additionally tolerates bracketed or plain comma-separated forms.

    :param value: The input value to be converted. Can be of the type `DbScalar`,
                  a sequence of `float`, or `None`.
    :return: A list of float values parsed from the input or `None` if the input
             is `None`.
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
