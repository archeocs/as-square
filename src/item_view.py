from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from object_dict import ObjectDict as od

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

    def clear(self):
        self.seth(self.widget, '')

def comboBox(items):
    cb = QComboBox()
    cb.addItem('Undefined', '')
    for it in items:
        cb.addItem(it.displayText, userData=it.key)
    return cb

def setCurrentKey(combo, key):
    keyIndex = combo.findData(key)
    if keyIndex < 0:
        combo.setCurrentIndex(0)
    combo.setCurrentIndex(keyIndex)

def getCurrentKey(combo):
    return combo.currentData()

def listEditor(label, items):
    cb = comboBox(items)
    return AttrEditor(label, cb,
                      setHandler=setCurrentKey,
                      getHandler=getCurrentKey)

def textEditor(label):
    return AttrEditor(label, QLineEdit())

class ItemFormWidget(QWidget):
    def __init__(self, log, parent=None):
        QWidget.__init__(self, parent)
        self.input = od({})
        self.lay = QFormLayout(parent)
        self.log = log

    def addText(self, name, label):
        ed = textEditor(label)
        self.input[name] = ed
        self.lay.addRow(ed.label, ed.widget)

    def addList(self, name, label, items):
        ed = listEditor(label, items)
        self.input[name] = ed
        self.lay.addRow(ed.label, ed.widget)

    def setItem(self, item):
        self.log.info('Set item {}', item)
        for ed in self.input.values():
            ed.clear()
        if not item:
            return
        for (edName, ed) in self.input.items():
            v = item.value(edName)
            if v:
                ed.setValue(v)

    def mergeItem(self, item):
        for (edName, ed) in self.input.items():
            v = ed.value()
            if v:
                self.log.info('Merge {}:{}', edName,  v)
                item.setValue(edName, ed.value())
        return item
