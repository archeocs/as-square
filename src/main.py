from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qgis.core import *
from functools import partial
from layers_manager import LayersManager
from item_view import ItemFormWidget

class LogAdapter:

    def info(self, message, *args):
        pass

class StdOutLogAdapter(LogAdapter):

    def info(self, message, *args):
        if args == ():
            print(message)
        else:
            print(message.format(*args))        

def formWidget(log, parent):
    form = ItemFormWidget(log, parent)
    form.addText('square_id', 'Square')
    form.addText('survey_date', 'Date')
    form.addText('azp', 'AZP number')
    form.addText('people', 'People')
       
    form.addText('pottery', 'Pottery')
    form.addText('glass', 'Glass')
    form.addText('bones', 'Bones')
    form.addText('metal', 'Metal')
    form.addText('flint', 'Flint')
    form.addText('clay', 'Clay')
    form.addText('other', 'Other')
    form.addItemEditor('sources',
                       'Classification',
                       {'ZB': 'OWR', 'SC': 'Wcz. Śred C',
                         'SD': 'Wcz. Śred D', 'SE': 'Wcz. Śred E',
                         'SF': 'Wcz. Śred F',
                         'SP': 'Późne Śred', 'N': 'Nowożytność',
                         'N0': 'XX w.', '':None},
                       {'NLJ':'KPL', 'NAK': 'KAK', 'BLZ': 'Łużycka', '':None})
    form.addText('author', 'Author')
    form.addText('s_remarks', 'Source remarks')

    form.addText('observation', 'Observation')
    form.addText('temperature', 'Temperature')
    form.addText('weather', 'Weather')
    form.addText('plow_depth', 'Plow Depth')
    form.addText('agro_treatments', 'Agricultural Treatments')
    form.addText('remarks', 'Remarks')
    return form

class AsSquareWidget(QDockWidget):
    def __init__(self, log, iface, parent=None):
        QDockWidget.__init__(self, parent=parent)
        self.log = log
        self.iface = iface
        wgt = QWidget()
        lay = QVBoxLayout(self)
        self.status = QStatusBar(self)
        self.form = formWidget(log, wgt)
        lay.addWidget(self.createActions(['Add', 'Update']))
        lay.addWidget(self.form)
        lay.addWidget(self.status, alignment=Qt.AlignBottom)
        wgt.setLayout(lay)
        self.actionsMap['Add'].pressed.connect(self.addAction)
        self.actionsMap['Update'].pressed.connect(self.updateAction)

        self.setWidget(wgt)

        self.layersMgr = LayersManager(QgsProject.instance(),
                                       self.log,
                                       lambda x: QgsVectorLayer(x, providerLib='spatialite'))
        self.layersMgr.handlers['item_selected'] = self.form.setItem
        self.layersMgr.handlers['records_removed'] = self.recordsRemoved
        self.log.info('Initialized')

    def recordsRemoved(self):
        self.iface.messageBar().pushMessage('Removed layer AS_RECORD. Please add layer to project',
                                            Qgis.Warning)
        self.form.setItem(None)

    def addAction(self):
        itNew = self.form.mergeItem(self.layersMgr.selectedItem())
        if self.layersMgr.isReady():
            self.layersMgr.addItem(itNew)
        else:
            self.iface.messageBar().pushMessage('''Can't add new record.
            Check if layer AS_RECORDS is added to project and try again''',
                                            Qgis.Warning)

    def updateAction(self):
        itUpdt = self.form.mergeItem(self.layersMgr.selectedItem())
        self.layersMgr.updateItem(itUpdt)

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
    panel = AsSquareWidget(log, iface, parent)
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
