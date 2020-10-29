from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qgis.core import *

class Plugin(object):

    def __init__(self,iface):
        self.iface = iface
    
    def initGui(self):
        self.qgisAction = QAction("Asquare", self.iface.mainWindow())
        self.qgisAction.setWhatsThis("Layers List")
        self.qgisAction.setStatusTip("Layers List")
        self.qgisAction.triggered.connect(self.run)

        self.iface.addToolBarIcon(self.qgisAction)
        self.iface.addPluginToMenu("Asquare",self.qgisAction)

    def unload(self):
        self.iface.removePluginMenu('Asquare', self.qgisAction)
        self.iface.removeToolBarIcon(self.qgisAction)
        #self.iface.removeDocWidget(self.dockWidget)
        
    def run(self):
        self.dockWidget = start(self.iface.mainWindow(), iface=self.iface)

class LogAdapter:

    def info(self, message):
        pass

class StdOutLogAdapter(LogAdapter):

    def info(self, message):
        print(message)

class QgsLogAdapter(LogAdapter):

    def __init__(self, name):
        self.name = name

    def info(self, message):
        QgsMessageLog.logMessage(message, self.name, level=Qgis.Info)

def getLayer(name):
    proj = QgsProject.instance()
    upperName = name.upper()
    for v in proj.mapLayers().values():
        if v.isValid() and v.type() == QgsMapLayer.VectorLayer and str(v.name()).upper() == upperName:
            return v
    return None
        
class AsquareWidget(QDockWidget):

    def __init__(self, log, iface, parent=None):
        QDockWidget.__init__(self, parent=parent)
        self.log = log
        self.iface = iface
        wgt = QWidget()
        lay = QVBoxLayout(self)
        self.status = QStatusBar(self)
        lay.addWidget(self.createActions(['Add', 'Analyze']))
        lay.addWidget(self.status, alignment=Qt.AlignBottom)
        wgt.setLayout(lay)
        self.actionsMap['Add'].pressed.connect(self.addAction)
        self.actionsMap['Analyze'].pressed.connect(self.showAction)
        self.setWidget(wgt)
        self.initLayers()
        self.log.info('Initialized')

    def initLayers(self):
        self.targetLayer = getLayer('stanowiska')
        if not self.targetLayer:
            QgsProject.instance().layersAdded.connect(self.setTargetLayer)
        self.sourceLayer = getLayer('grid50')
        if not self.sourceLayer:
            QgsProject.instance().layersAdded.connect(self.setSourceLayer)
        
    def setSourceLayer(self, layers):
        if self.sourceLayer:
            return
        for m in layers:
            if m.type() == QgsMapLayer.VectorLayer and str(m.name()).upper() == 'GRID50':
                self.sourceLayer = m
                self.log.info('Source layer ' + m.name())
                return

    def setTargetLayer(self, layers):
        if self.targetLayer:
            return
        for m in layers:
            if m.type() == QgsMapLayer.VectorLayer and str(m.name()).upper() == 'STANOWISKA':
                self.targetLayer = m
                self.log.info('Target layer ' + m.name())
                return
        
    def addAction(self):
        selected = self.sourceLayer.selectedFeatureIds()
        if len(selected) == 1:
            feat = self.sourceLayer.getFeature(selected[0])
            self.status.showMessage('Add action')
        elif len(selected) > 1:
            self.log.info('Multi selection')

    def showAction(self):
        self.status.showMessage('Show action')

    def createActions(self, actions):
        self.actionsMap = {}
        actionsGroup = QDialogButtonBox(self)
        for a in actions:
            btn = actionsGroup.addButton(a,QDialogButtonBox.ActionRole)
            self.actionsMap[a] = btn
        return actionsGroup

def start(parent, iface=None, app=None):
    log = None
    if iface:
        log = QgsLogAdapter('Asquare')
    else:
        log = StdOutLogAdapter()
    panel = AsquareWidget(log, iface, parent)
    if iface:
        iface.currentLayerChanged.connect(lambda x: print(x))
        iface.addDockWidget( Qt.RightDockWidgetArea, panel )
    elif app:
        window = QMainWindow()
        window.setCentralWidget(panel)
        window.show()
        app.exec_()
    return panel

def main():
    from sys import argv
    app = QApplication(argv)
    start(None, None, app)

if __name__ == '__main__':
    main()
