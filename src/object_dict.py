# Copyright (C) Miłosz Pigłas <milosz@archeocs.com>
#
# Licensed under the European Union Public Licence

from collections import UserDict

class ObjectDict(UserDict):

    def __init__(self, initData={}):
        UserDict.__init__(self, initData)

    def __getattr__(self, name):
        if name in self.data:
            return self.data[name]
        raise AttributeError('object has no attribute ' + name)
