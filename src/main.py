from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qgis.core import *

TARGET_LAYER = 'AS_SQUARES'

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

    def getFeature(self, target):
        if not self.feat:
            return None
        allFields = target.fields()
        f = QgsFeature(allFields)
        for a in allFields.names():
            self.log.info('field ' + str(a))
            if a.lower() in self.input:
                ta = self.input[a.lower()].text().strip()
                if ta:
                    self.log.info(str(a) + ' = ' + str(ta))
                    f[a] = ta
        f.setGeometry(self.feat.geometry())
        return f
        

class AsquareWidget(QDockWidget):

    def __init__(self, log, iface, parent=None):
        QDockWidget.__init__(self, parent=parent)
        self.log = log
        self.iface = iface
        wgt = QWidget()
        lay = QVBoxLayout(self)
        self.status = QStatusBar(self)
        self.form = FeatureForm(self.log, self)
        lay.addWidget(self.createActions(['Add', 'Analyze']))
        lay.addWidget(self.form)
        lay.addWidget(self.status, alignment=Qt.AlignBottom)
        wgt.setLayout(lay)
        self.actionsMap['Add'].pressed.connect(self.addAction)
        self.actionsMap['Analyze'].pressed.connect(self.showAction)
        self.setWidget(wgt)
        self.initLayers()
        self.log.info('Initialized')

    def initLayers(self):
        self.targetLayer = getLayer(TARGET_LAYER)
        if not self.targetLayer:
            QgsProject.instance().layersAdded.connect(self.setTargetLayer)
        self.sourceLayer = getLayer('grid50')
        if not self.sourceLayer:
            QgsProject.instance().layersAdded.connect(self.setSourceLayer)
        else:
            self.sourceLayer.selectionChanged.connect(self.featuresSelected)

    def featuresSelected(self, selected, deselected, clear):
        if len(selected) == 1:
            feat = self.sourceLayer.getFeature(selected[0])
            self.form.setFeature(feat)
        elif len(selected) > 1:
            self.form.clear()
            self.log.info('Multiselect')
        else:
            self.form.clear()
            
    def setSourceLayer(self, layers):
        if self.sourceLayer:
            return
        for m in layers:
            if m.type() == QgsMapLayer.VectorLayer and str(m.name()).upper() == 'GRID50':
                self.sourceLayer = m
                self.sourceLayer.selectionChanged.connect(self.featuresSelected)
                self.log.info('Source layer ' + m.name())
                return

    def setTargetLayer(self, layers):
        if self.targetLayer:
            return
        for m in layers:
            if m.type() == QgsMapLayer.VectorLayer and str(m.name()).upper() == TARGET_LAYER:
                self.targetLayer = m
                self.log.info('Target layer ' + m.name())
                return

    def addAction(self):
        self.targetLayer.startEditing()
        fnew = self.form.getFeature(self.targetLayer)
        if not fnew:
            self.log.info('Nothing to add')
            return
        self.targetLayer.addFeature(fnew)
        saved = self.targetLayer.commitChanges()
        count = self.targetLayer.featureCount()
        if saved:
            self.log.info('Feature added: ' + str(saved) + '. Count: ' + str(count))
        else:
            self.log.info('Errors ' + str(self.targetLayer.commitErrors()))
        
    def addAction2(self):
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
