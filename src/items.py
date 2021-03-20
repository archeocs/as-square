# Copyright (C) Miłosz Pigłas <milosz@archeocs.com>
#
# Licensed under the European Union Public Licence

EXCLUDE_NAMES = ['id']

class GeoItem:

    def __init__(self, attrs, geom, ident=None, sourceType='grid'):
        self.attrs = attrs
        self.geometry = geom
        self.ident = ident
        self.sourceType = sourceType

    def value(self, name):
        ln = name.lower()
        if ln in self.attrs and ln not in EXCLUDE_NAMES:
            return self.attrs[ln]
        return None

    def setValue(self, name, v):
        ln = name.lower()
        if ln in self.attrs and ln not in EXCLUDE_NAMES:
            self.attrs[ln] = v


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
