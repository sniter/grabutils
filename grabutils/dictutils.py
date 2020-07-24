class dictview:

    def __init__(self, data, *path, inline=True):
        self.data = data
        self.inline = inline
        self.path = path

    @property
    def value(self):
        return self.data

    # @value.setter
    # def value(self, value):
    #     self.data = value

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return self.__str__()

    def __get_value(self, item):
        if not self.data:
            ret = self.data
        elif isinstance(self.data, dict):
            ret = self.data.get(item)
        elif isinstance(self.data, list) or isinstance(self.data, tuple):
            ret = self.data[item] if len(self.data) > int(item) else None
        elif isinstance(self.data, set):
            ret = item if item in self.data else None
        else:
            ret = self.data.__getitem__(item)
        if self.inline:
            self.data = ret
            return self
        else:
            return dictview(ret)

    def __getitem__(self, item) -> 'dictview':
        return self.__get_value(item)

    def __getattr__(self, item) -> 'dictview':
        return self.__get_value(item)
