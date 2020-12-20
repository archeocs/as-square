from sys import argv

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

X_TYPE = QMetaType.User + 100

class Cell:

    def __init__(self, display, key, ctype):
        self.displayText = display
        self.editText = key
        if not key:
            self.editText = display
        self.ctype = ctype

    def __str__(self):
        return 'd={}, k={}'.format(self.displayText, self.editText)

class InputTabWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setCentralWidget(self.createView())

    def createView(self):
        tab = QTableView(self)
        model = self.createModel([[Cell('A', 'a', X_TYPE)]])
        tab.setModel(model)
        tab.setItemDelegateForColumn(0, mapComboBoxDelegate({'a': 'A', 'b': 'B'}))
        return tab

    def createModel(self, rows):
        model = QStandardItemModel(0, len(rows[0]))
        for r in rows:
            mrow = list(map(newItem, r))
            model.appendRow(mrow)
        return model

def newItem(value):
    sit = TypedItem(value.ctype)
    sit.setEditable(True)
    sit.setData(value.displayText, role=Qt.DisplayRole)
    sit.setData(value.editText, role=Qt.EditRole)
    return sit

def mapComboBoxDelegate(options):
    delegate = MapComboBoxDelegate(options) 
    return delegate

class MapComboBoxDelegate(QStyledItemDelegate):

    def __init__(self, options, parent=None):
        QStyledItemDelegate.__init__(self, parent)
        self.options = options

    def createEditor(self, parent, opts, index):
        cb = MapComboBox(parent)
        for (k, v) in self.options.items():
            cb.addItem(v, userData=k)
        return cb

    def setEditorData(self, ed, index):
        v = index.data(Qt.EditRole)
        ed.setKey(v)

    def setModelData(self, ed, model, index):
        v = ed.key()
        model.setData(index, v, role=Qt.EditRole)
        model.setData(index, ed.itemData(ed.currentIndex(), Qt.DisplayRole), role=Qt.DisplayRole)

class MapComboBox(QComboBox):

    def __init__(self, parent=None):
        QComboBox.__init__(self, parent)

    def setKey(self, k):
        print('set key ', k)
        self.setCurrentIndex(self.findData(k))

    def key(self):
        return self.itemData(self.currentIndex())

class TypedItem(QStandardItem):

    def __init__(self, t):
        QStandardItem.__init__(self)
        self._type = t
        self.variants = {}

    def type(self):
        return self._type

    def setData(self, v, role=Qt.UserRole + 1):
        print('set data', v, role)
        self.variants[role] = v
        self.emitDataChanged()

    def data(self, role=Qt.UserRole + 1):
        v = self.variants.get(role, QVariant())
        return v

def main():
    app = QApplication(argv)
    win = InputTabWindow()
    win.show()
    app.exec_()

if __name__ == '__main__':
    main()
