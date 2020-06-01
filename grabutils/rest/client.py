import logging
from abc import ABC

from urllib.parse import urljoin, urlencode, quote_plus

import requests


class Field:
    pass


class Dto(ABC):
    _fields = tuple()

    @classmethod
    def __is_field(cls, f: str) -> bool:
        clz = getattr(cls, f).__class__
        return issubclass(clz, Field)

    @classmethod
    def init_dto(cls):
        cls._fields = tuple(f for f in dir(cls) if cls.__is_field(f)) + tuple([cls.key_field()])
        cls.__slot__ = cls._fields + tuple([
            '__modified',

        ])

    @classmethod
    def key_field(cls) -> str:
        return "id"

    def key_exists(self) -> bool:
        return hasattr(self, self.key_field())

    def get_key(self):
        return getattr(self, self.key_field())

    def __init__(self, data: dict):
        super().__init__()
        if data:
            self.update(**data)

    def items(self, full=False) -> iter:
        for f in self._fields:
            if f in self._fields:
                if not hasattr(self, f):
                    if full:
                        yield f, None
                    else:
                        pass
                else:
                    yield f, getattr(self, f)

    def to_dict(self) -> dict:
        return dict(self.items())

    def update(self, **data):
        for f in data:
            if f in self._fields:
                setattr(self, f, data[f])


class Endpoint:
    logger = logging.getLogger(__name__)

    def __init__(self, base, **params):
        self.base = base
        self.params = params

    def __repr__(self):
        if not self.params:
            return self.base
        return self.base + "?" + urlencode(self.params, quote_via=quote_plus)

    def __call__(self, *context, **params):
        paramz = dict(self.params)
        paramz.update(**params)
        return Endpoint(urljoin(self.base + '/', '/'.join(map(quote_plus, map(str, context))), **paramz))

    def __getattr__(self, key: str):
        if key in {'get', 'post', 'put', 'delete'}:
            logger = self.logger
            url = self.base

            def wrap(*args, **kwargs):
                logger.debug(f"{key.upper()} {url}")
                method = getattr(requests, key)
                return method(url, *args, **kwargs)

            return wrap
        return Endpoint(urljoin(self.base + '/', key), **self.params)
