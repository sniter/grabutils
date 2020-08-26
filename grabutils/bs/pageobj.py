import functools as fn
import operator as op

from bs4 import BeautifulSoup, Tag


class BsField:
    def __init__(self, selector, *then, src_attr='page', many=False):
        self.src_attr = src_attr
        self.selector = selector
        self.many = many
        self.then = then

    def __call__(self, node):
        then = self.then

        if self.many:
            res = node.select(self.selector) if self.selector else node
            return [
                fn.reduce(lambda v, func: func(v), then, r)
                for r in res
                if r
            ] if then else res

        else:
            res = node.select_one(self.selector) if self.selector else node
            return fn.reduce(lambda v, func: func(v), then, res) if then and res else res

    def __get__(self, obj, owner):
        if not (obj and isinstance(obj, BsPageObj) or isinstance(obj, PageObject)):
            return self

        if isinstance(obj, BsPageObj):
            page = obj.page()
        else:
            page = obj.as_source()
        then = self.then

        return self.__call__(page)


class PageObjMeta(type):
    def __new__(mcs, name, bases, attrs):
        klass = super().__new__(mcs, name, bases, attrs)

        fields = set(
            field_name
            for field_name, field
            in attrs.items()
            if (
                isinstance(field, BsField) or
                (callable(field) and field_name.startswith('attr_')) or
                not (
                    field_name.startswith('_') or
                    field_name == 'Meta' or
                    callable(field)
                )

            )
        )

        meta = klass.Meta

        meta_fields = getattr(meta, 'fields') if hasattr(meta, 'fields') else None
        meta_ignore_fields = getattr(meta, 'ignore_fields') if hasattr(meta, 'ignore_fields') else None
        meta_parser = getattr(meta, 'parser') if hasattr(meta, 'parser') else 'lxml'

        if meta_fields and meta_ignore_fields:
            raise Exception('Both attributes *fields* and *ignore_fields* are declared in Meta class ')

        if meta_fields:
            fields &= set(meta_fields)

        if meta_ignore_fields:
            fields -= set(meta_ignore_fields)

        klass._parser = meta_parser
        klass._export_fields = tuple(fields)
        return klass


class PageObject(metaclass=PageObjMeta):

    def __init__(self, page: str):
        if isinstance(page, BeautifulSoup) or isinstance(page, Tag):
            self.__page = page
        else:
            self.__page = BeautifulSoup(str(page), features=self._parser)
        self.__value = None

    def as_source(self):
        return self.__page

    def __extract_key(self, field):
        attr = getattr(self, field)
        if callable(attr):
            return field.replace('attr_', ''), attr(self.__page)

        return field, attr

    def as_dict(self):
        if not self.__value:
            self.__value = dict(
                self.__extract_key(field)
                for field
                in self._export_fields
            )
        return self.__value

    class Meta:
        parser: str = 'lxml'
        fields: tuple = None
        ignore_fields: tuple = None


class BsPageObj:

    @staticmethod
    def parser() -> str:
        return 'lxml'

    @staticmethod
    def system_fields() -> tuple:
        return 'parser', 'as_dict', 'page'

    @staticmethod
    def ignore_fields() -> tuple:
        return tuple()

    @classmethod
    def transient_attrs(cls) -> set:
        return set(cls.system_fields() + cls.ignore_fields())

    def __init__(self, page: str):
        if isinstance(page, BeautifulSoup) or isinstance(page, Tag):
            self.__page = page
        else:
            self.__page = BeautifulSoup(str(page), features=self.parser())
        self.__class_fields = None

    def page(self):
        return self.__page

    def as_dict(self):
        # list of BsFields (from class)
        class_fields = set(
            fld
            for fld, inst
            in self.__class__.__dict__.items()
            if isinstance(inst, BsField)
        )

        transient_attrs = self.transient_attrs()

        return dict(
            (field, getattr(self, field))
            for field
            in dir(self)
            if
            (
                field in class_fields or
                field not in transient_attrs

            ) and
            not field.startswith('_') and
            not field[0].isupper() and
            not callable(getattr(self, field))
        )


class Nested:
    def __init__(self, page_obj_clazz):
        self.page_obj_clazz = page_obj_clazz

    def __call__(self, value):
        return self.page_obj_clazz(value).as_dict()


inner_text = op.attrgetter('string')
stripped = op.methodcaller('strip')


def as_attr(attr, default=None):
    def as_attr_wrapper(node):
        return node.attrs.get(attr, default)

    return as_attr_wrapper


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
        return text + value if isinstance(value, str) else value

    return wrapper


class Href(BsField):
    def __init__(self, selector, *then, **kwargs):
        super(Href, self).__init__(selector, parse_href, *then, **kwargs)


class Image(BsField):
    def __init__(self, selector, **kwargs):
        super(Image, self).__init__(selector, parse_img, **kwargs)


class List:
    def __init__(self, field: BsField):
        self.field = field

    def __call__(self, node):
        return self.field.__call__(node)
