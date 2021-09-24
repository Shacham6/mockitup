class MethProxy:

    def __init__(self, attr_name, meth_cb):
        self.__attr_name = attr_name
        self.__meth_cb = meth_cb

    def __call__(self):
        return MethCallProxy(self.__attr_name, self.__meth_cb)


class MethCallProxy:

    def __init__(self, attr_name, cb):
        self.__attr_name = attr_name
        self.__cb = cb

    def returns(self, value):
        self.__cb(value)
