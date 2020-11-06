from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qgis.core import *
from functools import partial
from layers_manager import LayersManager

class LogAdapter:

    def info(self, message, *args):
        pass

class StdOutLogAdapter(LogAdapter):

    def info(self, message, *args):
        if args == ():
            print(message)
        else:
            print(message.format(*args))

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
        self.addText('survey_date', 'Date')
        self.addText('azp', 'AZP number')
        self.addText('people', 'People')
        self.lay.addRow(QRubberBand(QRubberBand.Line, self))
        self.addText('pottery', 'Pottery')
        self.addText('glass', 'Glass')
        self.addText('bones', 'Bones')
        self.addText('metal', 'Metal')
        self.addText('flint', 'Flint')
        self.addText('clay', 'Clay')
        self.addText('other', 'Other')
        self.addText('chronology', 'Chronology')
        self.addText('culture', 'Culture')
        self.addText('author', 'Author')
        self.addText('s_remarks', 'Source remarks')
        self.lay.addRow(QRubberBand(QRubberBand.Line, self))
        self.addText('observation', 'Observation')
        self.addText('temperature', 'Temperature')
        self.addText('weather', 'Weather')
        self.addText('plow_depth', 'Plow Depth')
        self.addText('agro_treatements', 'Agricultural Treatments')
        self.addText('remarks', 'Remarks')

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
            square['square_dimension'] = self.feat['square_dimension']
            square.setGeometry(self.feat.geometry())
            self.log.info('Set geometry {}',
                          square.geometry().asWkt())
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
        self.mainWidget = start_plugin(self.iface.mainWindow(), iface=self.iface)

def start_plugin(parent, iface):
    log = QgsLogAdapter('as-square')
    panel = AsquareWidget(log, iface, parent)
    iface.currentLayerChanged.connect(lambda x: print(x))
    iface.addDockWidget( Qt.RightDockWidgetArea, panel )
    return panel
    
def start(parent, iface=None, app=None):
    log = StdOutLogAdapter()
    panel = AsquareWidget(log, iface, parent)
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
