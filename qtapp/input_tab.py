from sys import argv

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class InputTabWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setCentralWidget(self.createView())

    def createView(self):
        tab = QTableView(self)
        model = QStandardItemModel(10, 10)
        tab.setModel(model)
        return tab


def main():
    app = QApplication(argv)
    win = InputTabWindow()
    win.show()
    app.exec_()

if __name__ == '__main__':
    main()
