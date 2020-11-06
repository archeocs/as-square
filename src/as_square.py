from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qgis.core import *

from main import LogAdapter
from main import AsquareWidget

class QgsLogAdapter(LogAdapter):

    def __init__(self, name):
        self.name = name

    def info(self, message, *args):
        msg = message
        if args:
            msg = message.format(*args)
        QgsMessageLog.logMessage(msg, self.name, level=Qgis.Info)

class Plugin:

    def __init__(self,iface):
        self.iface = iface
    
    def initGui(self):
        self.qgisAction = QAction("as-square", self.iface.mainWindow())
        self.qgisAction.triggered.connect(self.run)

        self.iface.addToolBarIcon(self.qgisAction)
        self.iface.addPluginToMenu("as-square",self.qgisAction)

    def unload(self):
        self.iface.removePluginMenu('as-square', self.qgisAction)
        self.iface.removeToolBarIcon(self.qgisAction)
        
    def run(self):
        self.start(self.iface.mainWindow(), iface=self.iface)

    def start(self, parent, iface):
        log = QgsLogAdapter('as-square')
        panel = AsquareWidget(log, iface, parent)
        iface.currentLayerChanged.connect(lambda x: print(x))
        iface.addDockWidget( Qt.RightDockWidgetArea, panel )

