import math


def vector_sub(a: tuple[float, float], b: tuple[float, float]) -> tuple[float, float]:
    return a[0] - b[0], a[1] - b[1]


def vector_add(a: tuple[float, float], b: tuple[float, float], w: float = 1.0) -> tuple[float, float]:
    return a[0] + b[0] * w, a[1] + b[1] * w


def vector_norm(a: tuple[float, float]) -> float:
    return math.sqrt(a[0] ** 2 + a[1] ** 2)


def vector_normalize(a: tuple[float, float]) -> tuple[float, float]:
    norm = vector_norm(a)
    if norm < 1e-4:
        return 0, 0
    return a[0] / norm, a[1] / norm


def vector_dist(a: tuple[float, float], b: tuple[float, float]) -> float:
    return vector_norm(vector_sub(a, b))
