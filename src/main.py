from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qgis.core import *
from functools import partial
from layers_manager import LayersManager
from item_view import ItemFormWidget
from migration import *
import os

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

        self.checkDbAction = QAction('Check DB version', self.iface.mainWindow())
        self.checkDbAction.triggered.connect(self.checkDb)

        self.migrateDbAction = QAction('Migrate Database', self.iface.mainWindow())
        self.migrateDbAction.triggered.connect(self.migrateDb)

        self.iface.addPluginToMenu('as-square', self.checkDbAction)
        self.iface.addPluginToMenu('as-square', self.migrateDbAction)

    def unload(self):
        self.iface.removePluginMenu('as-square', self.qgisAction)
        self.iface.removeToolBarIcon(self.qgisAction)
        
    def run(self):
        self.mainWidget = start_plugin(self.iface.mainWindow(), iface=self.iface)

    def migrateDb(self):
        log = QgsLogAdapter('migrate db')
        selectedDb = QInputDialog.getItem(self.iface.mainWindow(),
                                          'Migrated Database version',
                                          'Select database to migrate',
                                          self.dbList(log),
                                          editable=False)
        if selectedDb[1]:
            log.info('selected: {} {}', selectedDb[0], os.path.dirname(__file__))
            base = os.path.dirname(__file__)
            scriptPath = os.path.join(base, 'assquare-migration-db.sql' )
            result = migrateDb(selectedDb[0], scriptPath)
            if not result[0]:
                self.iface.messageBar().pushMessage('Database migration failed '
                                                    + str(result[2]),
                                                    level=Qgis.Info)
            elif result[1] is None:
                self.iface.messageBar().pushMessage('Database up to date', level=Qgis.Info)
            else:
                self.iface.messageBar().pushMessage('Database migrated to version '
                                                    + str(result[1]),
                                                    level=Qgis.Info)

    def checkDb(self):
        log = QgsLogAdapter('check db')
        selectedDb = QInputDialog.getItem(self.iface.mainWindow(),
                                          'Check DB version',
                                          'Select database to check',
                                          self.dbList(log),
                                          editable=False)
        if selectedDb[1]:
            log.info('selected: {} {}', selectedDb[0], os.path.dirname(__file__))
            base = os.path.dirname(__file__)
            scriptPath = os.path.join(base, 'assquare-migration-db.sql' )
            check = checkDb(selectedDb[0], scriptPath)
            log.info('check result {}', check)
            if check:
                if check[0] == check[1]:
                    self.iface.messageBar().pushMessage('Database up to date', level=Qgis.Info)
                elif check[0] < check[1]:
                    self.iface.messageBar().pushMessage(
                        'Database at version {}. Expected version {}'.format(
                            check[0], check[1]), level=Qgis.Info)
            else:
                self.iface.messageBar().pushMessage('Check error', level=Qgis.Info)

    def dbList(self, log):
        allDb = []
        settings = QgsSettings()
        settings.beginGroup('SpatiaLite/connections')
        for k in settings.allKeys():
            if k.endswith('path'):
                log.info('{} {}', k, settings.value(k))
                allDb.append(settings.value(k))
        return allDb

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
