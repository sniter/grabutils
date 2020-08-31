from functools import reduce


class Project:
    def __init__(self, *path, **kwargs):
        self.path = path
        self.field = kwargs.get('field')
        self.silent = kwargs.get('silent', False)
        self.default = kwargs.get('default')
        self.conv = kwargs.get('astype')
        # self.allow_none = kwargs.get('allow_none', True)

    @staticmethod
    def get_field(obj, field, silent, default) -> (bool, any):
        if hasattr(obj, '__getitem__'):
            try:
                return False, obj[field]
            except KeyError as ke:
                if not silent:
                    raise ke
                return True, default
        elif isinstance(field, str) and hasattr(obj, field):
            return False, getattr(obj, field)

    def iter_path(self, obj, field):
        is_done, old_obj = obj
        if not is_done:
            return self.get_field(old_obj, field, self.silent, self.default)
        return obj

    def __call__(self, obj):
        was_failed, content = reduce(self.iter_path, self.path, (False, obj))
        return self.conv(content) if self.conv else content

    def __get__(self, obj, owner) -> any:
        if hasattr(obj, '_get_data'):
            return self(getattr(obj, '_get_data')())
        else:
            return self


class Zip(Project):

    def __init__(self, left: Project, right: Project, **kwargs):
        super(Zip, self).__init__(*[left, right], **kwargs)
        self.conv = self.conv or list

    def __call__(self, obj):
        return self.conv(zip(*[el(obj) for el in self.path]))


class Callable(Project):

    def __init__(self, fn, **kwargs):
        super(Callable, self).__init__(fn, **kwargs)

    def __call__(self, obj):
        content = self.path[0](obj)

        return self.conv(content) if self.conv else content

    def __get__(self, obj, owner) -> any:
        if hasattr(obj, '_get_data'):
            return self(getattr(obj, '_get_data')())
        else:
            return self




class ObjectViewMeta(type):
    def __new__(mcs, name, bases, attrs):
        klass = super().__new__(mcs, name, bases, attrs)

        dynamic_fields = set()

        for field_name, field in attrs.items():
            if isinstance(field, Project):
                field.field = field_name
            elif callable(field) and field_name.startswith('attr_'):
                dynamic_fields.add(field_name.replace('attr_', ''))

        fields = set(
            field_name
            for field_name, field
            in attrs.items()
            if (
                isinstance(field, Project) or
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

        if meta_fields and meta_ignore_fields:
            raise Exception('Both attributes *fields* and *ignore_fields* are declared in Meta class ')

        if meta_fields:
            fields &= set(meta_fields)

        if meta_ignore_fields:
            fields -= set(meta_ignore_fields)

        klass._export_fields = tuple(fields)
        klass._dynamic_fields = dynamic_fields
        return klass


class ObjectView(metaclass=ObjectViewMeta):
    def __init__(self, data):
        self.__data = data
        # for fld, fn in self._dynamic_fields.items():
        #     setattr(self, fld, Callable(fn))

    def _get_data(self):
        return self.__data

    def __getattr__(self, item):
        if item in self._dynamic_fields:
            return getattr(self, 'attr_' + item)(self.__data)
        return super(ObjectView, self).__getattribute__(item)

    class Meta:
        fields = []
        ignore_fields = []
