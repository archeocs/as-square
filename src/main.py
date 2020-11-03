from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qgis.core import *
from functools import partial
from layers_manager import LayersManager

SQUARES_LAYER = 'AS_SQUARES'
SOURCES_LAYER = 'AS_SOURCES'
VIEW_LAYER = 'AS_RECORDS'
GRID_LAYER = 'GRID50'

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

    def info(self, message, *args):
        pass

class StdOutLogAdapter(LogAdapter):

    def info(self, message, *args):
        if args == ():
            print(message)
        else:
            print(message.format(*args))

class QgsLogAdapter(LogAdapter):

    def __init__(self, name):
        self.name = name

    def info(self, message, *args):
        msg = message
        if args:
            msg = message.format(*args)
        QgsMessageLog.logMessage(msg, self.name, level=Qgis.Info)

def getLayer(name):
    proj = QgsProject.instance()
    upperName = name.upper()
    for v in proj.mapLayers().values():
        if v.isValid() and v.type() == QgsMapLayer.VectorLayer and str(v.name()).upper() == upperName:
            return v
    return None

class FeatureForm(QWidget):

    def __init__(self, log, parent=None):
        QWidget.__init__(self, parent)
        self.log = log
        self.lay = QFormLayout()
        self.setLayout(self.lay)
        self.input = {}
        self.feat = None
        self.addText('square_id', 'Square')
        self.addText('name', 'Name')
        self.addText('collected', 'Date')
        self.addText('location', 'Location')
        self.addText('area_no', 'Area Number')
        self.lay.addRow(QRubberBand(QRubberBand.Line, self))
        self.addText('pottery', 'Pottery')
        self.addText('glass', 'Glass')
        self.addText('bones', 'Bones')
        self.addText('metal', 'Metal')
        self.addText('flint', 'Flint')
        self.addText('clay', 'Clay')
        self.addText('other', 'Other')
        self.lay.addRow(QRubberBand(QRubberBand.Line, self))
        self.addText('chronology', 'Chronology')
        self.addText('author', 'Author')
        self.addText('remarks', 'Remarks')
        self.lay.addRow(QRubberBand(QRubberBand.Line, self))
        self.addText('people', 'People')
        self.addText('observation', 'Observation')
        self.addText('accesibility', 'Accessibilty')
        self.addText('weather', 'Weather')

    def setFeature(self, feat):
        for f in self.input.values():
            f.clear()
        self.feat = feat
        if feat:
            names = feat.fields().names()
            for attr in names:
                if attr in self.input:
                    fv = feat[attr]
                    if isinstance(fv, str):
                        self.input[attr].setText(fv)
                else:
                    self.log.info('Attribute ignored: ' + str(attr))

    def clear(self):
        self.feat = None
        self.setFeature(None)
                
        
    def addText(self, key, label):
        txt = QLineEdit()
        self.lay.addRow(label, txt)
        self.input[key] = txt
        return txt

    def featureFromFields(self, layer):
        allFields = layer.fields()
        f = QgsFeature(allFields)
        fc = 0
        for a in allFields.names():
            self.log.info('field ' + str(a))
            if a.lower() in self.input:
                ta = self.input[a.lower()].text().strip()
                if ta:
                    self.log.info(str(a) + ' = ' + str(ta))
                    f[a] = ta
                    fc += 1
        if fc > 0:
            return f
        return None
    
    def getFeature(self, squares, artifacts):
        if not self.feat:
            return None
        square = self.featureFromFields(squares)
        art = self.featureFromFields(artifacts)
        if square:
            square.setGeometry(self.feat.geometry())
        return [square, art]
        

class AsquareWidget(QDockWidget):

    def __init__(self, log, iface, parent=None):
        QDockWidget.__init__(self, parent=parent)
        self.log = log
        self.iface = iface
        wgt = QWidget()
        lay = QVBoxLayout(self)
        self.status = QStatusBar(self)
        self.form = FeatureForm(self.log, self)
        lay.addWidget(self.createActions(['Add']))
        lay.addWidget(self.form)
        lay.addWidget(self.status, alignment=Qt.AlignBottom)
        wgt.setLayout(lay)
        self.actionsMap['Add'].pressed.connect(self.addAction)
        self.setWidget(wgt)

        self.layersMgr = LayersManager(QgsProject.instance(),
                                       self.log,
                                       lambda x: QgsVectorLayer(x, providerLib='spatialite'))
        self.layersMgr.handlers['grid_selected'] = self.form.setFeature
        self.log.info('Initialized')
                    
    def addAction(self):
        fnew = self.form.getFeature(self.layersMgr.squares,
                                    self.layersMgr.sources)
        if not fnew or not fnew[0]:
            self.log.info('Nothing to add')
            return
        self.layersMgr.addRecord(fnew[0], fnew[1])

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
