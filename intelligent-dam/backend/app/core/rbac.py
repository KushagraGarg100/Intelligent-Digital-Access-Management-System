from __future__ import annotations

from functools import wraps
from typing import Callable, TypeVar

from flask import jsonify
from flask_jwt_extended import get_jwt, verify_jwt_in_request


F = TypeVar("F", bound=Callable)


def require_roles(*roles: str) -> Callable[[F], F]:
    def decorator(fn: F) -> F:
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            role = claims.get("role")
            if role not in roles:
                return jsonify({"error": "forbidden", "required_roles": list(roles)}), 403
            return fn(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator

