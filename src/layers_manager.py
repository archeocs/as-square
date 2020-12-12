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
        self.item = None

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
        self.sources = None
        self.squares = None
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
        self.qgsProj.layerWillBeRemoved[QgsMapLayer].connect(
            partial(self.onLayerUnloaded,
                    name=VIEW_LAYER,
                    oper=self.removedViewLayer
                    )
        )

    def removedViewLayer(self, lay):
        self.log.info('Event: layer removed {}', lay.name())
        if self.records:
            self.squares = None
            self.sources = None
            self.records = None
            self.managed.remove(lay.name().upper())
            self.txManager.layers.clear()
            self.emit('records_removed')

    def isReady(self):
        return self.records and self.squares and self.sources

    def initDataLayers(self):
        self.log.info('Init data layers')
        self.records = self.getLayer(VIEW_LAYER)
        if self.records:
            self.squares = self.getOrLoad(SQUARES_LAYER, self.records, 'geometry')
            self.sources = self.getOrLoad(SOURCES_LAYER, self.records)
            self.addLayerAttrs(self.squares)
            self.addLayerAttrs(self.sources)
            self.managed.add(VIEW_LAYER)
            self.txManager.layers.append(self.squares)
            self.txManager.layers.append(self.sources)
            self.records.selectionChanged.connect(partial(self.gridSelected, layer=self.records))
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
            self.grid[name].selectionChanged.connect(partial(self.gridSelected, layer=self.grid[name]))
            self.log.info('Source layer {} initialized', name)
            return True
        return False

    def toItem(self, feat):
        self.log.info('Id: {}', feat.id())
        names = feat.fields().names()
        base = GeoItem(dict(self.baseAttrs), feat.geometry(), feat.id())
        for n in names:
            base.setValue(n, feat[n])
        self.log.info('Item {}', base.attrs)
        return base

    def gridSelected(self, selected, deselected, clear, layer):
        if len(selected) == 1:
            self.log.info('Selected')
            feat = layer.getFeature(selected[0])
            self.txManager.item = self.toItem(feat)
            self.emit('item_selected', self.txManager.item)
            self.emit('grid_selected', feat)
        elif len(selected) > 1:
            self.log.info('Multiselect')
            self.emit('grid_selected', None)
            self.emit('item_selected', None)
        else:
            self.emit('grid_selected', None)
            self.emit('item_selected', None)

    def emit(self, event, data=None):
        if event in self.handlers:
            if data:
                self.handlers[event](data)
            else:
                self.handlers[event]()

    def onLayerLoaded(self, layers, name, initFunc):
        """
        When layer with name matching argument 'name' is added
        then 'initFunc' is initialized.

        This method is supposed to be partialy initialized and
        attached to signal QgsProject.layersAdded.

        For example
        QgsProject.layerAdded.connect(partial(onLayerLoaded, name='layer-name', initFunc=lambda x: pass))

        First argument represents list of added layers
        and is received from signal
        """
        self.log.info('onLayerLoaded: {} {}', list(map(lambda x: x.name(), layers)), name)
        if name in self.managed:
            self.log.info('{} already managed {}', name, self.managed)
            return
        matching = filter(lambda v: equalIgnoreCase(v.name(), name) and isVector(v), layers)
        if len(list(matching)) > 0 and initFunc:
            self.log.info('Layer {} is loaded. Initialization started', name)
            initFunc()

    def onLayerUnloaded(self, layer, name, oper):
        self.log.info('Unload vent {} {}', layer.name(), name);
        if name.upper() not in self.managed:
            return
        elif layer.name().upper() != name.upper():
            return
        else:
            oper(layer)

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

    def selectedItem(self):
        if self.txManager.item:
            item = self.txManager.item
            return GeoItem(dict(item.attrs),
                           item.geometry, item.ident)
        return None

    def updateFeature(self, feat, item):
        """
        Merges feature with item values
        """
        for n in feat.fields().names():
            self.log.info('{}: {}', n, item.value(n))
            iv = item.value(n)
            if iv:
                feat[n] = iv
        self.log.info('updateFeature {}', feat.id())
        return feat


    def updateFeatureAttrs(self, item, layer):
        """
        Saves changed values in layer storage
        """
        allFields = layer.fields()
        for f in allFields:
            fid = allFields.indexOf(f.name())
            iv = item.value(f.name())
            if iv:
                layer.changeAttributeValue(item.ident, fid, iv)

    def updateItem(self, item):
        """
        Saves item in layer storage
        """
        self.txManager.begin()
        self.updateFeatureAttrs(item, self.squares)
        self.updateFeatureAttrs(item, self.sources)
        self.txManager.commit()
        self.log.info('Item updated {}', item.ident)

    def addItem(self, item):
        sqFeat = self.updateFeature(QgsFeature(self.squares.fields()), item)
        sqFeat.setGeometry(item.geometry)
        srcFeat = self.updateFeature(QgsFeature(self.sources.fields()), item)
        sqId = self.addRecord(sqFeat, srcFeat)
        item.ident = sqId
        self.txManager.item = item

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
            return
        if sourcesFeat:
            sourcesFeat['square'] = squareId
            sourcesFeat.setId(squareId)
            self.sources.addFeature(sourcesFeat)
        saved = self.txManager.commit()
        self.records.dataProvider().forceReload()
        count = self.records.featureCount()
        sqCount = self.squares.featureCount()
        if saved:
            self.log.info('Feature added: {}. Rec count: {}, Squares count: {} ', str(saved),  count, sqCount)
