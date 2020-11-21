from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from object_dict import ObjectDict as od
from items import *

class AttrEditor:

    def __init__(self, label, widget,
                 setHandler=lambda e, v: e.setText(str(v)),
                 getHandler=lambda e: e.text()):
        self.widget = widget
        self.geth = getHandler
        self.seth = setHandler
        self.label = label

    def value(self):
        return self.geth(self.widget)

    def setValue(self, v):
        self.seth(self.widget, v)

def textEditor(label):
    return AttrEditor(label, QLineEdit())

class ItemFormWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.input = od({})
        self.lay = QFormLayout(parent)

    def addText(self, name, label):
        ed = textEditor(label)
        self.input[name] = ed
        self.lay.addRow(ed.label, ed.widget)

    def setItem(self, item):
        for (edName, ed) in self.input.items():
            v = item.value(edName)
            if v:
                ed.setValue(v)
