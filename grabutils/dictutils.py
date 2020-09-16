import re
from contextlib import contextmanager


class dictview:

    def __init__(self, data, inline=False):
        self.__container_data = data
        self.inline = inline

    @property
    def value(self):
        return self.__container_data

    # @value.setter
    # def value(self, value):
    #     self.__container_data = value

    @property
    @contextmanager
    def value_ctx(self):
        yield self.__container_data

    def scan(self, path: str) -> 'dictview':
        """
        Scan

        Parameters
        ----------
        path : str
            specific path in current dictview, i.e. "path.to.the.content"

        Returns
        -------
        dictview
        """

        d = dictview(self.value, inline=True)
        for el in path.split('.'):
            if re.match(r'^\d+$', el):
                d = d[int(el)]
            else:
                d = d[el]
        d.inline = self.inline
        return d

    def project(self, **kwargs):
        return dict(
            (k, self.scan(path).value)
            for k, path in kwargs.items()
        )

    def __str__(self):
        return str(self.__container_data)

    def __repr__(self):
        return self.__str__()

    def __iter__(self):
        if hasattr(self.__container_data, '__iter__'):
            return self.__container_data.__iter__()

    def __len__(self):
        try:
            return self.__container_data.__len__()
        except:
            return 0

    def __get_value(self, item):
        if not self.__container_data:
            ret = self.__container_data
        elif hasattr(self.__container_data, item):
            ret = getattr(self.__container_data, item)
        elif hasattr(self.__container_data, '__getitem__') and isinstance(item, int):
            ret = self.__container_data.__getitem__(item)
        elif hasattr(self.__container_data, 'get'):
            ret = self.__container_data.get(item)
        elif isinstance(self.__container_data, set):
            ret = item if item in self.__container_data else None
        else:
            ret = None

        return self._wrap_output(ret)

    def __search(self, pattern: re.Pattern) -> list:
        if isinstance(self.__container_data, dict):
            return [v for k, v in self.__container_data.items() if pattern.search(k)]
        elif isinstance(self.__container_data, list) or isinstance(self.__container_data, tuple):
            return [v for v in self.__container_data if pattern.search(v)]
        elif isinstance(self.__container_data, set):
            return [v for v in self.__container_data if pattern.search(v)]
        else:
            return []

    def _wrap_output(self, output):
        if self.inline:
            self.__container_data = output
            return self

        return dictview(output, inline=self.inline)

    def __getitem__(self, item) -> 'dictview':
        if self.__container_data is None:
            return self._wrap_output(self.__container_data)

        if hasattr(self.__container_data, '__getitem__'):
            try:
                if isinstance(item, re.Pattern):
                    res = self.__search(item)
                else:
                    res = self.__container_data.__getitem__(item)
            except IndexError:
                res = None
            except KeyError:
                res = None

            return self._wrap_output(res)

        if item == '__container_data':
            return super(dictview, self).__getattr__(item)

        try:
            res = getattr(self.__container_data, item)
        except AttributeError:
            res = None

        return self._wrap_output(res)

    def __contains__(self, item) -> bool:
        if hasattr(self.__container_data, '__contains__'):
            return self.__container_data.__contains__(item)
        elif isinstance(item, str):
            return hasattr(self.__container_data, item)
        else:
            return False

    def __getattr__(self, item) -> 'dictview':
        assert isinstance(item, str)
        res = None
        finished = False

        if item == '__container_data':
            return super(dictview, self).__getattr__(item)

        if hasattr(self.__container_data, '__getitem__'):
            try:
                res = self.__container_data.__getitem__(item)
                finished = True
            except IndexError:
                finished = True
            except KeyError:
                finished = False

        if not finished:
            try:
                res = getattr(self.__container_data, item)
                finished = True
            except AttributeError:
                finished = False

        return self._wrap_output(res)
