"""Ejemplo mínimo para practicar pytest."""

from __future__ import annotations


def add(a: float, b: float) -> float:
    return a + b


def divide(a: float, b: float) -> float:
    if b == 0:
        raise ZeroDivisionError("b must be non-zero")
    return a / b


def clamp(value: float, low: float, high: float) -> float:
    if low > high:
        raise ValueError("low must be <= high")
    return max(low, min(high, value))
