from qgis.core import *
from functools import partial

SQUARES_LAYER = 'AS_SQUARES'
SOURCES_LAYER = 'AS_SOURCES'
VIEW_LAYER = 'AS_RECORDS'
GRID_LAYER = 'GRID50'


def isVector(lay):
    return lay.type() == QgsMapLayer.VectorLayer

def equalIgnoreCase(s1, s2):
    return s1.upper() == s2.upper()

def sameDb(v1, v2):
    c1 = v1.dataProvider().uri().database()
    c2 = v2.dataProvider().uri().database()
    return c1 == c2

class TxManager:

    def __init__(self):
        self.layers = []

    def begin(self):
        for e in self.layers:
            e.startEditing()

    def commit(self):
        for x in self.layers:
            if not x.commitChanges():
                self.log.info('Errors ' + str(x.commitErrors()))
                return False
        return True

class LayersManager:

    def __init__(self, qgsProj, log, layFactory):
        self.qgsProj = qgsProj
        self.log = log
        self.managed = set([])
        self.handlers = {}
        self.layFactory = layFactory
        self.txManager = TxManager()
        self.initRecordsLayer()
        self.initGridLayer()

    def initGridLayer(self):
        if not self.initGridEvents():
            self.qgsProj.layerAdded.connect(partial(self.onLayerLoaded, name=GRID_LAYER, initFunc=self.initGridEvents))
        
    def initRecordsLayer(self):
        if not self.initDataLayers():
            self.qgsProj.layerAdded.connect(partial(self.onLayerLoaded, name=VIEW_LAYER, initFunc=self.initDataLayers))

    def initDataLayers(self):        
        self.records = self.getLayer(VIEW_LAYER)
        if self.records:
            self.squares = self.getOrLoad(SQUARES_LAYER, self.records)
            self.sources = self.getOrLoad(SOURCES_LAYER, self.records)
            self.managed.add(VIEW_LAYER)
            self.txManager.layers.append(self.squares)
            self.txManager.layers.append(self.sources)
            return True
        return False

    def initGridEvents(self):
        self.grid = self.getLayer(GRID_LAYER)
        if self.grid:
            self.managed.add(GRID_LAYER)
            self.grid.selectionChanged.connect(self.gridSelected)
            return True
        return False

    def gridSelected(self, selected, deselected, clear):
        if len(selected) == 1:
            feat = self.grid.getFeature(selected[0])
            self.emit('grid_selected', feat)
        elif len(selected) > 1:
            self.log.info('Multiselect')
            self.emit('grid_selected', None)
        else:
            self.emit('grid_selected', None)

    def emit(self, event, data):
        self.handlers[event](data)
            
    def onLayerLoaded(self, layers, name, initFunc):
        if name in self.managed:
            return
        matching = filter(lambda v: equalIgnoreCase(v.name(), name) and isVector(v), layers)
        if matching and initFunc:
            self.log.info('Layer {} is loaded. Initialization started', name)
            initFunc()

    def getOrLoad(self, name, reference):
        v = self.getLayer(name, reference)
        if v:
            return v
        else:
            return self.loadLayer(reference.dataProvider().uri(), name)

    def loadLayer(self, uri, table):
        copy = QgsDataSourceUri(uri)
        copy.setTable(table)
        copy.setGeometryColumn(None)
        self.log.info('Loading layer ' + table + ' ' + copy.uri())
        return self.layFactory(copy.uri())
        
    
    def getLayer(self, name, otherLayer=None):
        stdName = name.upper()
        for v in self.qgsProj.mapLayers().values():
            if v.isValid() and isVector(v) and equalIgnoreCase(name, v.name()) and (not otherLayer or sameDb(otherLayer, v)):
                return v
        return None

    def addRecord(self, square, sourcesFeat):
        self.txManager.begin()
        squaresAdd = self.squares.dataProvider().addFeatures([square])
        squareId = None
        if squaresAdd[0]:
            squareId = squaresAdd[1][0].id()
            self.log.info('Added square with id {}', squareId)
        else:
            self.log.info('Adding Failed')
        if sourcesFeat:
            sourcesFeat['square'] = squareId
            self.sources.addFeature(sourcesFeat)
        saved = self.txManager.commit()
        self.records.dataProvider().forceReload()
        count = self.records.featureCount()
        sqCount = self.squares.featureCount()
        if saved:
            self.log.info('Feature added: {}. Rec count: {}, Squares count: {} ', str(saved),  count, sqCount)
