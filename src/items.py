
class AttrType:

    def __init__(self, name, plain=False, multi=False):
        self.plain = plain
        self.name = name

class StrAttr(AttrType):

    def __init__(self):
        AttrType.__init__(self, 'string')

class NumAttr(AttrType):

    def __init__(self):
        AttrType.__init__(self, 'number')

class ListAttr(AttrType):

    def __init__(self, values):
        AttrType.__init__(self, 'list', True, True)
        self._values = values

    def values(self):
        return self._values

class RefAttr(AttrType):

    def __init__(self, refName, refHandler):
        AttrType.__init__(self, 'ref', True, True)
        self.refName = refName
        self.rh = refHandler

    def values(self):
        return self.rh.allValues()

class ItemAttr:

    def __init__(self, name, atype, value=None, readOnly=False):
        self.name = name
        self.atype = atype
        self.value = value
        self.readOnly = readOnly

class GeoItem:

    def __init__(self, attrs, geom):
        self.attrs = attrs
        self.geometry = geom

    def value(self, name):
        if name in self.attrs:
            return self.attrs[name]
        return None

    def setValue(self, name, v):
        if name in self.attrs:
            self.attrs[name] = v


class Item:

    def __init__(self, attrs):
        self.attrs = attrs

    def value(self, name):
        if name in self.attrs:
            return self.attrs[name].value
        return None

    def atype(self, name):
        if name in self.attrs:
            return self.attrs[name].atype
        return None

    def readOnly(self, name):
        if name in self.attrs:
            return self.attrs[name].readOnly
        return False

    def setValue(self, name, v):
        if name in self.attrs:
            self.attrs[name].value = v
