from sys import argv

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class InputTabWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setCentralWidget(QTableWidget(5, 5))

def main():
    app = QApplication(argv)
    win = InputTabWindow()
    win.show()
    app.exec_()

if __name__ == '__main__':
    main()
