from qgis.core import *
from functools import partial

from items import *

SQUARES_LAYER = 'AS_SQUARES'
SOURCES_LAYER = 'AS_SOURCES'
VIEW_LAYER = 'AS_RECORDS'
GRID_LAYER = 'GRID_50_M'
GRID_10M_LAYER = 'GRID_10_M'

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
        self.grid = {}
        self.layFactory = layFactory
        self.txManager = TxManager()
        self.baseAttrs = {}
        ###################
        self.initRecordsLayer()
        self.initGridLayer()

    def initGridLayer(self):
        if not self.initEventsGrid50m():
            self.qgsProj.layersAdded.connect(partial(self.onLayerLoaded, name=GRID_LAYER, initFunc=self.initEventsGrid50m))
        if not self.initEventsGrid10m():
            self.qgsProj.layersAdded.connect(partial(self.onLayerLoaded, name=GRID_10M_LAYER, initFunc=self.initEventsGrid10m))
        
    def initRecordsLayer(self):
        if not self.initDataLayers():
            self.qgsProj.layersAdded.connect(partial(self.onLayerLoaded, name=VIEW_LAYER, initFunc=self.initDataLayers))

    def initDataLayers(self):        
        self.records = self.getLayer(VIEW_LAYER)
        if self.records:
            self.squares = self.getOrLoad(SQUARES_LAYER, self.records, 'geometry')
            self.sources = self.getOrLoad(SOURCES_LAYER, self.records)
            self.addLayerAttrs(self.squares)
            self.addLayerAttrs(self.sources)
            self.managed.add(VIEW_LAYER)
            self.txManager.layers.append(self.squares)
            self.txManager.layers.append(self.sources)
            return True
        return False

    def initEventsGrid50m(self):
        return self.initGridEvents(GRID_LAYER)

    def initEventsGrid10m(self):
        return self.initGridEvents(GRID_10M_LAYER)
    
    def initGridEvents(self, name):
        self.grid[name] = self.getLayer(name)
        if self.grid.get(name, None):
            self.managed.add(name)
            self.grid[name].selectionChanged.connect(partial(self.gridSelected, layer=name))
            self.log.info('Source layer {} initialized', name)
            return True
        return False

    def toItem(self, feat):
        self.log.info('{}', self.baseAttrs)
        names = feat.fields().names()
        base = GeoItem(dict(self.baseAttrs), feat.geometry())
        for n in names:
            base.setValue(n, feat[n])
        self.log.info('Item {}', base.attrs)
        return base

    def gridSelected(self, selected, deselected, clear, layer):
        if len(selected) == 1:
            self.log.info('Selected')
            feat = self.grid[layer].getFeature(selected[0])
            self.emit('grid_selected', feat)
            self.emit('item_selected', self.toItem(feat))
        elif len(selected) > 1:
            self.log.info('Multiselect')
            self.emit('grid_selected', None)
            self.emit('item_selected', None)
        else:
            self.emit('grid_selected', None)
            self.emit('item_selected', None)

    def emit(self, event, data):
        if event in self.handlers:
            self.handlers[event](data)
            
    def onLayerLoaded(self, layers, name, initFunc):
        if name in self.managed:
            return
        matching = filter(lambda v: equalIgnoreCase(v.name(), name) and isVector(v), layers)
        if len(list(matching)) > 0 and initFunc:
            self.log.info('Layer {} is loaded. Initialization started', name)
            initFunc()

    def addLayerAttrs(self, layer):
        for f in layer.fields().names():
            self.baseAttrs[f.lower()] = None

    def getOrLoad(self, name, reference, geocol=None):
        v = self.getLayer(name, reference)
        if not v:
            v = self.loadLayer(reference.dataProvider().uri(), name, geocol)
        return v

    def loadLayer(self, uri, table, geocol=None):
        copy = QgsDataSourceUri(uri)
        copy.setTable(table)
        copy.setGeometryColumn(geocol)
        self.log.info('Loading layer ' + table + ' ' + copy.uri())
        v = self.layFactory(copy.uri())
        if not v:
            raise Exception('Initialization with uri {} failed. Check layer factory'.format(copy.uri()))
        return v

    def getLayer(self, name, otherLayer=None):
        stdName = name.upper()
        for v in self.qgsProj.mapLayers().values():
            if v.isValid() and isVector(v) and equalIgnoreCase(name, v.name()) and (not otherLayer or sameDb(otherLayer, v)):
                return v
        self.log.info('Layer {} not found', name)
        return None

    def addRecord(self, square, sourcesFeat):
        self.txManager.begin()
        squaresAdd = self.squares.dataProvider().addFeatures([square])
        squareId = None
        if squaresAdd[0]:
            squareId = squaresAdd[1][0].id()
            self.log.info('Added square with id {}', squareId)
        else:
            self.log.info('Adding to {} Failed {}',
                          self.squares.dataProvider().uri().uri(),
                          square.geometry().asWkt())
        if sourcesFeat:
            sourcesFeat['square'] = squareId
            self.sources.addFeature(sourcesFeat)
        saved = self.txManager.commit()
        self.records.dataProvider().forceReload()
        count = self.records.featureCount()
        sqCount = self.squares.featureCount()
        if saved:
            self.log.info('Feature added: {}. Rec count: {}, Squares count: {} ', str(saved),  count, sqCount)
