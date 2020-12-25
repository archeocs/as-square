from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class Cell:

    def __init__(self, display, key=None):
        self.displayText = display
        self.editText = key

    def __str__(self):
        return 'd={}, k={}'.format(self.displayText, self.editText)


class Column:

    def __init__(self, allowedValues=None, empty='', hidden=False, label=None):
        self.allowed = allowedValues
        self.combo = allowedValues is not None
        self.empty = empty
        self.hidden = hidden
        self.label = label

    def modelItem(self, val):
        if self.combo and val in self.allowed:
            return newItem(Cell(self.allowed[val], val))
        else:
            return newItem(Cell(val))

    def getValue(self, item):
        if self.combo:
            print('get combo', item)
            return item.data(role=Qt.EditRole)
        else:
            return item.data(role=Qt.DisplayRole)

    def getEmpty(self):
        return self.modelItem(self.empty)

class InputTabWidget(QWidget):

    accepted = pyqtSignal()
    canceled = pyqtSignal()

    def __init__(self, modelDef, rows, parent=None):
        QWidget.__init__(self, parent)
        lay = QVBoxLayout()
        self.setLayout(lay)

        self.tab = self.initView(modelDef)
        self.model = self.initModel(modelDef, rows)
        self.tab.setModel(self.model)

        for (ci, c) in enumerate(modelDef):
            if c.combo:
                delegate = mapComboBoxDelegate(c.allowed, self.tab)
                self.tab.setItemDelegateForColumn(ci, delegate)
            if c.hidden:
                self.tab.hideColumn(ci)
        self.modelDef = modelDef

        lay.addWidget(self.tab)
        lay.addWidget(self.createButtons())

    def initView(self, modelDef):
        tab = QTableView(self)
        modelDef = modelDef
        return tab

    def initModel(self, modelDef, rows):

        model = QStandardItemModel(0, len(modelDef))
        model.setHorizontalHeaderLabels([md.label for md in modelDef])
        for r in rows:
            mrow = [modelDef[ci].modelItem(c)
                    for (ci, c) in enumerate(r)]
            model.appendRow(mrow)
        return model

    def addRowAction(self):
        self.model.appendRow([md.getEmpty()
                              for md in self.modelDef])

    def delRowAction(self):
        selModel = self.tab.selectionModel()
        if selModel.hasSelection():
            idx = selModel.currentIndex()
            self.model.removeRow(idx.row())

    def createButtons(self):
        buttons = QGroupBox(self)
        lay = QHBoxLayout()
        buttons.setLayout(lay)

        addBtn = QPushButton('+')
        addBtn.clicked.connect(self.addRowAction)

        delBtn = QPushButton('-')
        delBtn.clicked.connect(self.delRowAction)

        okBtn = QPushButton('OK')
        okBtn.clicked.connect(self.accepted.emit)

        cancelBtn = QPushButton('Cancel')
        cancelBtn.clicked.connect(self.canceled.emit)


        lay.addWidget(addBtn)
        lay.addWidget(delBtn)
        lay.addWidget(okBtn)
        lay.addWidget(cancelBtn)

        return buttons

    def getRows(self):
        allRows = []
        for rc in range(self.model.rowCount()):
            row = []
            for (ci, md) in enumerate(self.modelDef):
                sit = self.model.item(rc, ci)
                row.append(md.getValue(sit))
            allRows.append(row)
        return allRows

class InputTabDialog(QDialog):

    def __init__(self, modelDef, rows, parent):
        QDialog.__init__(self, parent)
        lay = QVBoxLayout()
        self.setLayout(lay)
        self.widget = InputTabWidget(modelDef, rows, self)
        lay.addWidget(self.widget)
        self.widget.accepted.connect(self.accept)
        self.widget.canceled.connect(self.reject)
        self.setModal(True)

    def getRows(self):
        return self.widget.getRows()



class InputTabWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        columns = [
            Column({'a': 'A', 'b': 'B', '?': ''}, empty='?')
            ,Column()
            ,Column()
            ,Column({'x': 'X', 'y': 'YYYYYY', '?': ''}, empty='?')
        ]
        rows = [
            ['a', '1111', '5555', 'y']
        ]
        self.setCentralWidget(InputTabWidget(columns, rows, self))

class StartWindow(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)
        btn = QPushButton('OPEN')
        btn.clicked.connect(self.start)
        self.setCentralWidget(btn)

    def start(self):
        columns = [ 
            Column({'a': 'A', 'b': 'B', '?': ''}, empty='?')
            ,Column()
            ,Column(label='Middle')
            ,Column({'x': 'X', 'y': 'YYYYYY', '?': ''}, empty='?')
            ,Column(empty=None, hidden=True)
        ]
        rows = [
            ['a', '1111', '5555', 'y', 1]
        ]
        itd = InputTabDialog(columns, rows, self)
        v = itd.exec_()
        print(v)
        if v == 1:
            print(itd.getRows())

def newItem(value):
    print(value)
    if value.editText:
        sit = TypedItem()
        sit.setData(value.editText, role=Qt.EditRole)
    else:
        sit = QStandardItem()
    sit.setEditable(True)
    sit.setData(value.displayText, role=Qt.DisplayRole)
    return sit

def mapComboBoxDelegate(options, parent):
    delegate = MapComboBoxDelegate(options, parent) 
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
        display = ed.itemData(ed.currentIndex(), Qt.DisplayRole)
        model.setData(index, display, role=Qt.DisplayRole)

class MapComboBox(QComboBox):

    def __init__(self, parent=None):
        QComboBox.__init__(self, parent)

    def setKey(self, k):
        self.setCurrentIndex(self.findData(k))

    def key(self):
        return self.itemData(self.currentIndex())

class TypedItem(QStandardItem):

    def __init__(self):
        QStandardItem.__init__(self)
        self.variants = {}

    def setData(self, v, role=Qt.UserRole + 1):
        self.variants[role] = v
        self.emitDataChanged()

    def data(self, role=Qt.UserRole + 1):
        v = self.variants.get(role, QVariant())
        return v

def main():
    from sys import argv

    app = QApplication(argv)
    win = StartWindow()
    win.show()
    app.exec_()

if __name__ == '__main__':
    main()
