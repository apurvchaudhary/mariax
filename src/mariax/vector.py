import json
from typing import Iterable, List, Optional


def validate_vector(vec: Iterable[float], dim: Optional[int] = None) -> List[float]:
    if vec is None:
        raise ValueError("vector must not be None")
    try:
        arr = [float(x) for x in vec]
    except Exception as e:
        raise ValueError("vector must be an iterable of numbers") from e
    if dim is not None and len(arr) != dim:
        raise ValueError(f"expected vector dim={dim}, got {len(arr)}")
    return arr


def to_db_text(vec: Iterable[float], dim: Optional[int] = None) -> str:
    arr = validate_vector(vec, dim)
    return json.dumps(arr)


def from_db_value(value) -> Optional[List[float]]:
    if value is None:
        return None
    if isinstance(value, (list, tuple)):
        return [float(x) for x in value]
    if isinstance(value, (bytes, str)):
        s = value.decode() if isinstance(value, bytes) else value
        try:
            return [float(x) for x in json.loads(s)]
        except Exception:
            s2 = s.strip("[]() ")
            if not s2:
                return []
            return [float(x) for x in s2.split(",") if x.strip()]
    return [float(value)]
