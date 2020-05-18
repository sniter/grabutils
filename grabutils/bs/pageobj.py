import functools as fn

from bs4 import BeautifulSoup


class BsField:
    def __init__(self, selector, *then, src_attr='page', many=False):
        self.src_attr = src_attr
        self.selector = selector
        self.many = many
        self.then = then

    def __get__(self, obj, owner):
        page = obj.page()
        then = self.then

        if self.many:
            res = page.select(self.selector)
            return [
                fn.reduce(lambda v, func: func(v), then, r)
                for r in res
                if r
            ] if then else res

        else:
            res = page.select_one(self.selector)
            return fn.reduce(lambda v, func: func(v), then, res) if then and res else res


class BsPageObj:
    parser = 'lxml'
    _persist = False
    _enqueue = False

    def __init__(self, page: str):
        if isinstance(page, BeautifulSoup):
            self.__page = page
        else:
            self.__page = BeautifulSoup(str(page), features=self.parser)

    def page(self):
        return self.__page

    def as_dict(self):
        class_fields = set(
            fld
            for fld, inst
            in self.__class__.__dict__.items()
            if isinstance(inst, BsField)
        )

        return dict(
            (field, getattr(self, field))
            for field
            in dir(self)
            if
            (
                field in class_fields or
                field not in {'as_dict', 'page', 'persist', 'enqueue'}

            ) and
            not field.startswith('_') and
            not field[0].isupper() and
            not callable(getattr(self, field))
        )

    @classmethod
    def persist(cls) -> bool:
        return cls._persist

    def enqueue(self, func, **kwargs):
        pass


class Nested:
    def __init__(self, page_obj_clazz):
        self.page_obj_clazz = page_obj_clazz

    def __call__(self, value):
        return self.page_obj_clazz(value).as_dict()


def parse_href(node):
    return dict(
        href=node.attrs['href'],
        label=node.string.strip()
    )


def parse_img(node):
    return dict(
        src=node.attrs['src'],
        label=node.attrs.get('alt') if node else None
    )


def prepend(text: str):
    def wrapper(value: str):
        return text + value

    return wrapper


class Href(BsField):
    def __init__(self, selector, *then, **kwargs):
        super(Href, self).__init__(selector, parse_href, *then, **kwargs)


class Image(BsField):
    def __init__(self, selector, **kwargs):
        super(Image, self).__init__(selector, parse_img, **kwargs)
