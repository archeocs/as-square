# Copyright (C) Miłosz Pigłas <milosz@archeocs.com>
#
# Licensed under the European Union Public Licence

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qgis.core import *
from functools import partial
from layers_manager import LayersManager
from item_view import ItemFormWidget
from migration import *
from lang import tr
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
    form.addText('square_id', tr('square.id'))
    form.addText('survey_date', tr('survey.date'))
    form.addText('azp', tr('azp.number'))
    form.addText('people', tr('people'))
       
    form.addText('pottery', tr('pottery'))
    form.addText('glass', tr('glass'))
    form.addText('bones', tr('bones'))
    form.addText('metal', tr('metal'))
    form.addText('flint', tr('flint'))
    form.addText('clay', tr('clay'))
    form.addText('other', tr('other'))
    form.addItemEditor('sources',
                       tr('classification'),
                       {'ZB': 'OWR', 'SC': 'Wcz. Śred C',
                         'SD': 'Wcz. Śred D', 'SE': 'Wcz. Śred E',
                         'SF': 'Wcz. Śred F',
                         'SP': 'Późne Śred', 'N': 'Nowożytność',
                         'N0': 'XX w.', '':None},
                       {'NLJ':'KPL', 'NAK': 'KAK', 'BLZ': 'Łużycka', '':None})
    form.addText('author', tr('author'))
    form.addText('s_remarks', tr('source_remarks'))

    form.addText('observation', tr('observation'))
    form.addText('temperature', tr('temperature'))
    form.addText('weather', tr('weather'))
    form.addText('plow_depth', tr('plow_depth'))
    form.addText('agro_treatments', tr('agro_treat'))
    form.addText('remarks', tr('remarks'))
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
        lay.addWidget(self.createActions(['save_item', 'reset_item']))
        lay.addWidget(self.form)
        lay.addWidget(self.status, alignment=Qt.AlignBottom)
        wgt.setLayout(lay)
        self.actionsMap['save_item'].pressed.connect(self.saveAction)
        self.actionsMap['reset_item'].pressed.connect(self.resetAction)
        self.setWidget(wgt)

        self.layersMgr = LayersManager(QgsProject.instance(),
                                       self.log,
                                       lambda x: QgsVectorLayer(x, providerLib='spatialite'))
        self.layersMgr.handlers['item_selected'] = self.form.setItem
        self.layersMgr.handlers['records_removed'] = self.recordsRemoved
        self.log.info('Initialized')

    def recordsRemoved(self):
        self.iface.messageBar().pushMessage(tr('removed_as_records_warning'),
                                            Qgis.Warning)
        self.form.setItem(None)

    def resetAction(self):
        selected = self.layersMgr.selectedItem()
        if selected:
            self.form.setItem(selected)

    def saveAction(self):
        selected = self.layersMgr.selectedItem()
        if selected and self.layersMgr.isReady():
            itSave = self.form.mergeItem(selected)
            if selected.sourceType == 'grid':
                self.layersMgr.addItem(itSave)
            elif selected.sourceType == 'squares':
                self.layersMgr.updateItem(itSave)
        elif not self.layersMgr.isReady():
            self.iface.messageBar().pushMessage(tr('missing_as_records_warning'),
                                            Qgis.Warning)
        else:
            self.log.info('No items selected')

    def createActions(self, actions):
        self.actionsMap = {}
        actionsGroup = QDialogButtonBox(self)
        for a in actions:
            btn = actionsGroup.addButton(tr(a), QDialogButtonBox.ActionRole)
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

        self.checkDbAction = QAction(tr('check_db_action'), self.iface.mainWindow())
        self.checkDbAction.triggered.connect(self.checkDb)

        self.migrateDbAction = QAction(tr('migrate_db_action'), self.iface.mainWindow())
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
                                          tr('migrate_db_message'),
                                          tr('migrate_db_select_db'),
                                          self.dbList(log),
                                          editable=False)
        if selectedDb[1]:
            log.info('selected: {} {}', selectedDb[0], os.path.dirname(__file__))
            base = os.path.dirname(__file__)
            scriptPath = os.path.join(base, 'as-square-migration-db.sql' )
            result = migrateDb(selectedDb[0], scriptPath)
            if not result[0]:
                self.iface.messageBar().pushMessage(tr('migrate_db_error')
                                                    + ' ' + str(result[2]),
                                                    level=Qgis.Info)
            elif result[1] is None:
                self.iface.messageBar().pushMessage(tr('migrate_db_up_to_date_info'), level=Qgis.Info)
            else:
                self.iface.messageBar().pushMessage(tr('migrate_db_success')
                                                    + ' ' + str(result[1]),
                                                    level=Qgis.Info)

    def checkDb(self):
        log = QgsLogAdapter('check db')
        selectedDb = QInputDialog.getItem(self.iface.mainWindow(),
                                          tr('check_db_message'),
                                          tr('check_db_select'),
                                          self.dbList(log),
                                          editable=False)
        if selectedDb[1]:
            log.info('selected: {} {}', selectedDb[0], os.path.dirname(__file__))
            base = os.path.dirname(__file__)
            scriptPath = os.path.join(base, 'as-square-migration-db.sql' )
            check = checkDb(selectedDb[0], scriptPath)
            log.info('check result {}', check)
            if check:
                if check[0] == check[1]:
                    self.iface.messageBar().pushMessage(tr('check_db_up_to_date'), level=Qgis.Info)
                elif check[0] < check[1]:
                    self.iface.messageBar().pushMessage(
                        tr('check_db_result').format(
                            check[0], check[1]), level=Qgis.Info)
            else:
                self.iface.messageBar().pushMessage(tr('check_db_error'), level=Qgis.Info)

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
