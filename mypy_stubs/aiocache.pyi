from typing import Any, Callable, Optional, Type

import aiocache.serializers as serializers  # noqa: I250
from aiocache.backends.redis import RedisCache
from aiocache.base import SENTINEL
from aiocache.factory import Cache, caches

class cached:
    def __init__(
        self,
        ttl: int = SENTINEL,
        key: Optional[str] = None,
        key_builder: Optional[Callable[..., str]] = None,
        cache: Type = Cache.MEMORY,
        serializer: Optional[Type] = None,
        plugins: Optional[list[Type]] = None,
        alias: Optional[str] = None,
        noself: bool = False,
        **kwargs: Any,
    ): ...
    def __call__(self, f: Callable[..., Any]) -> Callable[..., Any]: ...

__all__ = ("caches", "cached", "RedisCache", "serializers")
