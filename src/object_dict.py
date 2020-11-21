from collections import UserDict

class ObjectDict(UserDict):

    def __init__(self, initData={}):
        UserDict.__init__(self, initData)

    def __getattr__(self, name):
        if name in self.data:
            return self.data[name]
        raise AttributeError('object has no attribute ' + name)
