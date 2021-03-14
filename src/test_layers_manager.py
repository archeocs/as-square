import unittest

from qgis.core import *
from layers_manager import *
from items import GeoItem
from main import StdOutLogAdapter

MULTI_POLYGON_WKT = 'MultiPolygon (((387625 516820, 387675 516820, 387675 516770, 387625 516770, 387625 516820)))'
POLYGON_WKT = 'Polygon ((387625 516820, 387675 516820, 387675 516770, 387625 516770, 387625 516820))'

class TestSignal:

    def __init__(self):
        self.handlers = []

    def connect(self, fun):
        self.handlers.append(fun)

    def emit(self, *args):
        for f in self.handlers:
            f(*args)

    def __getitem__(self, n):
        return self

class QgsProj:

    def __init__(self, layers):
        self.layers = layers
        self.layersAdded = TestSignal()
        self.layerRemoved = TestSignal()
        self.layerWillBeRemoved = TestSignal()

    def mapLayers(self):
        return self.layers

    def testAddLayer(self, name, lay):
        self.layers[name] = lay
        self.layersAdded.emit([lay])

    def testRemoveLayer(self, name):
        del self.layers[name]
        self.layerWillBeRemoved.emit(Layer(name=name))

class DataProvider:

    def __init__(self, db):
        self._db = db
        self.features = []
        self.attrChanges = []

    def database(self):
        return self._db

    def uri(self):
        return QgsDataSourceUri(self._db)

    def forceReload(self):
        pass
    
    def addFeatures(self, f):
        self.features.extend(f)
        f[0].setId(1234)
        return (True, f)

RECORDS_URI = 'dbname=\'test.sqlite\' table="AS_SQUARES" (geometry) sql='

class Layer:

    def __init__(self, valid=True,
                 type=QgsMapLayer.VectorLayer,
                 name='AS_SQUARES',
                 db=RECORDS_URI,
                 fields = []):
        self._valid = valid
        self._type = type
        self._name = name
        self._dataProvider = DataProvider(db)
        self.selectionChanged = self
        self.handlers = {}
        self._fields = QgsFields()
        for f in fields:
            self._fields.append(QgsField(f, typeName='int'))

    def getFeatures(self, expr):
        return []

    def getFeature(self, args):
        return args
        
    def connect(self, fun):
        self.handlers['selection_changed'] = fun
        
    def isValid(self):
        return self._valid

    def type(self):
        return self._type

    def name(self):
        return self._name

    def dataProvider(self):
        return self._dataProvider

    def addFeature(self, f):
        self._dataProvider.addFeatures([f])

    def featureCount(self):
        return len(self._dataProvider.features)

    def startEditing(self):
        pass

    def commitChanges(self):
        return True

    def reload(self):
        pass

    def fields(self):
        return self._fields

    def changeAttributeValue(self, featId, fieldId, value):
        self._dataProvider.attrChanges.append((featId, fieldId, value))

def defaultLayerFactory(name):
    return Layer(name=name)

class LayersManagerTest(unittest.TestCase):

    def test_init_layer_is_loaded(self):
        qgsProj = QgsProj(layers={'AS_SQUARES': Layer(), 'grid_50_m': Layer(name='grid_50_m')})
        man = LayersManager(qgsProj, StdOutLogAdapter(), defaultLayerFactory)
        self.assertEqual(man.managed, {'AS_SQUARES', 'GRID_50_M'})

    def test_init_layer_selection_event_attached(self):
        qgsProj = QgsProj(layers={'AS_SQUARES': Layer(), 'grid_50_m': Layer(name='grid_50_m')})
        feats = []
        man = LayersManager(qgsProj, StdOutLogAdapter(), defaultLayerFactory)
        man.handlers['grid_selected'] = lambda x: feats.append(x)
        
        testFeat = self.feat()
        qgsProj.layers['grid_50_m'].handlers['selection_changed']([testFeat],'b','c')

        self.assertEqual(feats[0].id(), testFeat.id())

    def test_init_layer_selection_event_attached_grid_10_m(self):
        qgsProj = QgsProj(layers={'AS_SQUARES': Layer(), 'grid_10_m': Layer(name='grid_10_m')})
        feats = []
        man = LayersManager(qgsProj, StdOutLogAdapter(), defaultLayerFactory)
        man.handlers['grid_selected'] = lambda x: feats.append(x)

        testFeat = self.feat()
        qgsProj.layers['grid_10_m'].handlers['selection_changed']([testFeat],'b','c')

        self.assertEqual(feats, [testFeat])

    def test_init_layer_selection_event_attached_all_grids(self):
        qgsProj = QgsProj(layers={'AS_SQUARES': Layer(), 'grid_10_m': Layer(name='grid_10_m'), 'grid_50_m': Layer(name='grid_50_m')})
        feats = []
        man = LayersManager(qgsProj, StdOutLogAdapter(), defaultLayerFactory)
        man.handlers['grid_selected'] = lambda x: feats.append(x)

        feat10 = self.feat()
        feat50 = self.feat()

        qgsProj.layers['grid_10_m'].handlers['selection_changed']([feat10],'b','c')
        qgsProj.layers['grid_50_m'].handlers['selection_changed']([feat50],'b','c')

        self.assertEqual(feats, [feat10, feat50])

    def test_selected_feature_item_event_triggered(self):
        qgsProj = QgsProj(layers={'AS_SQUARES': Layer(),
                                  'grid_50_m': Layer(name='grid_50_m')})
        items = []
        man = LayersManager(qgsProj, StdOutLogAdapter(), defaultLayerFactory)
        man.handlers['item_selected'] = lambda x: items.append(x)

        expected_fields = dict([(f, '') for f in RECORD_ATTRS])
        feat_item = self.feat_item(fields=expected_fields)

        qgsProj.layers['grid_50_m'].handlers['selection_changed']([feat_item[0]],'b','c')

        self.assertEqual(items[0].ident, feat_item[1].ident)
        self.assertDictEqual(items[0].attrs, feat_item[1].attrs)
        self.assertEqual(items[0].sourceType, 'grid')

    def test_selected_record_item_event_triggered(self):
        qgsProj = QgsProj(layers={'AS_SQUARES': Layer(),
                                  'grid_50_m': Layer(name='grid_50_m')})
        items = []
        man = LayersManager(qgsProj, StdOutLogAdapter(), defaultLayerFactory)
        man.handlers['item_selected'] = lambda x: items.append(x)
        expected_fields = dict([(f, '') for f in RECORD_ATTRS])
        feat_item = self.feat_item(fields=expected_fields)

        qgsProj.layers['AS_SQUARES'].handlers['selection_changed']([feat_item[0]],'b','c')

        self.assertEqual(items[0].ident, feat_item[1].ident)
        self.assertDictEqual(items[0].attrs, feat_item[1].attrs)
        self.assertEqual(items[0].sourceType, 'squares')

    def test_selected_feature_current_item(self):
        qgsProj = QgsProj(layers={'AS_SQUARES': Layer(),
                                  'grid_50_m': Layer(name='grid_50_m')})
        items = []
        man = LayersManager(qgsProj, StdOutLogAdapter(), defaultLayerFactory)
        man.handlers['item_selected'] = lambda x: items.append(x)

        feat_item = self.feat_item()
        qgsProj.layers['grid_50_m'].handlers['selection_changed']([feat_item[0]],'b','c')

        current = man.selectedItem()
        self.assertEqual(current.ident, feat_item[1].ident)
        self.assertEqual(current.sourceType, 'grid')

    def test_selected_record_current_item(self):
        qgsProj = QgsProj(layers={'AS_SQUARES': Layer(),
                                  'grid_50_m': Layer(name='grid_50_m')})
        items = []
        man = LayersManager(qgsProj, StdOutLogAdapter(), defaultLayerFactory)
        man.handlers['item_selected'] = lambda x: items.append(x)

        feat_item = self.feat_item()
        qgsProj.layers['AS_SQUARES'].handlers['selection_changed']([feat_item[0]],'b','c')

        current = man.selectedItem()
        self.assertEqual(current.ident, feat_item[1].ident)
        self.assertEqual(current.sourceType, 'squares')


    def test_init_layer_sources_loaded(self):
        src = []
        def layerFactory(s):
            src.append(s)
            return QgsVectorLayer(s, providerLib='test')
        qgsProj = QgsProj(layers={'AS_SQUARES': Layer(), 'grid50': Layer(name='grid50')})
        man = LayersManager(qgsProj, StdOutLogAdapter(), layerFactory)
        print(src)
        self.assertTrue(isinstance(man.sources, QgsVectorLayer))
        self.assertEqual(src[0], RECORDS_URI
                         .replace('SQUARES','SOURCES')
                         .replace(' (geometry)', ''))

    def test_records_added_layer_loaded(self):
        qgsProj = QgsProj(layers={'grid_50_m': Layer(name='grid_50_m')})
        man = LayersManager(qgsProj, StdOutLogAdapter(), lambda x: Layer(name=x) )

        qgsProj.testAddLayer('AS_SQUARES', Layer())
        
        self.assertEqual(man.managed, {'AS_SQUARES', 'GRID_50_M'})

    def test_records_removed_and_added_again(self):
        qgsProj = QgsProj(layers={'AS_SQUARES': Layer(), 'grid_50_m': Layer(name='grid_50_m')})
        man = LayersManager(qgsProj, StdOutLogAdapter(), defaultLayerFactory)
        self.assertTrue(man.isReady())

        qgsProj.testRemoveLayer('AS_SQUARES')
        self.assertFalse(man.isReady())

        qgsProj.testAddLayer('AS_SQUARES', Layer())
        self.assertTrue(man.isReady())

    def test_grid_added_layer_loaded(self):
        qgsProj = QgsProj(layers={'AS_SQUARES': Layer()})
        man = LayersManager(qgsProj, StdOutLogAdapter(), defaultLayerFactory)

        qgsProj.testAddLayer('Grid_50_m', Layer(name='Grid_50_m'))
        
        self.assertEqual(man.managed, {'AS_SQUARES', 'GRID_50_M'})

    def test_grid_10_added_layer_loaded(self):
        qgsProj = QgsProj(layers={'AS_SQUARES': Layer()})
        man = LayersManager(qgsProj, StdOutLogAdapter(), defaultLayerFactory)

        qgsProj.testAddLayer('Grid_10_m', Layer(name='Grid_10_m'))
        
        self.assertEqual(man.managed, {'AS_SQUARES', 'GRID_10_M'})
        
    def test_records_added_layer_sources_loaded(self):
        src = []
        def layerFactory(s):
            src.append(s)
            return QgsVectorLayer(s, providerLib='test')
        qgsProj = QgsProj(layers={'grid_50_m': Layer(name='grid_50_m')})
        man = LayersManager(qgsProj, StdOutLogAdapter(), layerFactory)

        qgsProj.testAddLayer('AS_SQUARES', Layer())

        self.assertTrue(isinstance(man.sources, QgsVectorLayer))
        self.assertEqual(src[0], RECORDS_URI.replace('SQUARES','SOURCES').replace(' (geometry)', ''))

    def test_records_removed_manager_reset(self):
        qgsProj = QgsProj(layers={'AS_SQUARES': Layer(), 'grid_50_m': Layer(name='grid_50_m')})
        man = LayersManager(qgsProj, StdOutLogAdapter(), defaultLayerFactory)

        self.assertTrue(man.isReady())

        qgsProj.testRemoveLayer('AS_SQUARES')

        self.assertIsNone(man.sources)

    def test_records_removed_event_emited(self):
        qgsProj = QgsProj(layers={'AS_SQUARES': Layer(), 'grid_50_m': Layer(name='grid_50_m')})
        man = LayersManager(qgsProj, StdOutLogAdapter(), defaultLayerFactory)

        self.assertTrue(man.isReady())

        emited = False
        def eh():
            print('emited')
            nonlocal emited
            emited = True

        man.handlers['records_removed'] = eh 

        qgsProj.testRemoveLayer('AS_SQUARES')

        self.assertTrue(emited)

    def test_add_record(self):
        def layerFactory(s):
            return Layer(name=s)
        qgsProj = QgsProj(layers={'AS_SQUARES': Layer(), 'grid_50_m': Layer(name='grid_50_m')})
        man = LayersManager(qgsProj, StdOutLogAdapter(), layerFactory)

        man.addRecord(self.feat(), [self.feat()])

        self.assertEqual(len(man.sources.dataProvider().features), 1)
        self.assertEqual(len(man.squares.dataProvider().features), 1)
        self.assertEqual(man.sources.dataProvider().features[0]['square'], 1234)

    def test_add_item(self):
        def layerFactory(s):
            return Layer(name=s)
        qgsProj = QgsProj(layers={'AS_SQUARES': Layer(fields=['square']),
                                  'as_sources': Layer(name='as_sources', fields=['square']),
                                  'grid_50_m': Layer(name='grid_50_m')})
        man = LayersManager(qgsProj, StdOutLogAdapter(), layerFactory)

        man.addItem(GeoItem({'square': 1111, 'sources': [{'culture': 'XXX'}]}, geom=QgsGeometry()))

        self.assertEqual(len(man.sources.dataProvider().features), 1)
        self.assertEqual(len(man.squares.dataProvider().features), 1)
        self.assertEqual(man.sources.dataProvider().features[0]['square'], 1234)
        self.assertEqual(man.squares.dataProvider().features[0]['square'], 1111)

    def test_add_item_copy_polygon_geometry(self):
        def layerFactory(s):
            return Layer(name=s)
        qgsProj = QgsProj(layers={'AS_SQUARES': Layer(),
                                  'as_sources': Layer(name='as_sources', fields=['square']),
                                  'grid_50_m': Layer(name='grid_50_m')})
        man = LayersManager(qgsProj, StdOutLogAdapter(), layerFactory)
        man.addItem(GeoItem({'square': 1111, 'sources': [{'culture': 'XXX'}]},
                            geom=QgsGeometry.fromWkt(POLYGON_WKT)))

        self.assertEqual(len(man.squares.dataProvider().features), 1)
        wkt = man.squares.dataProvider().features[0].geometry().asWkt()
        self.assertEqual(wkt, POLYGON_WKT)

    def test_add_item_convert_multipart_polygon(self):
        def layerFactory(s):
            return Layer(name=s)
        qgsProj = QgsProj(layers={'AS_SQUARES': Layer(),
                                  'as_sources': Layer(name='as_sources', fields=['square']),
                                  'grid_50_m': Layer(name='grid_50_m')})
        man = LayersManager(qgsProj, StdOutLogAdapter(), layerFactory)
        man.addItem(GeoItem({'square': 1111, 'sources': [{'culture': 'XXX'}]},
                            geom=QgsGeometry.fromWkt(MULTI_POLYGON_WKT)))

        self.assertEqual(len(man.squares.dataProvider().features), 1)
        wkt = man.squares.dataProvider().features[0].geometry().asWkt()
        self.assertEqual(wkt, POLYGON_WKT)


    def test_update_item(self):
        def layerFactory(s):
            return Layer(name=s)
        qgsProj = QgsProj(layers={'AS_SQUARES': Layer(fields=['square']),
                                  'as_sources': Layer(name='as_sources', fields=['square']),
                                  'grid_50_m': Layer(name='grid_50_m')})
        man = LayersManager(qgsProj, StdOutLogAdapter(), layerFactory)

        man.updateItem(GeoItem({'square': 1111, 'sources': []}, geom=QgsGeometry(), ident=4444))

        self.assertIn((4444, 0, 1111), man.squares.dataProvider().attrChanges)

    def feat(self, fields={'square': 5}, geometry=POLYGON_WKT):
        ff = QgsFields()
        for (k, v) in fields.items():
            ff.append(QgsField(k, typeName=str(type(v))))
        qf = QgsFeature(ff)
        for (k, v) in fields.items():
            qf[k] = v
        qf.setId(12345)
        qf.setGeometry(QgsGeometry.fromWkt(geometry))
        return qf

    def feat_item(self, fields={'square': 5}, sources=[]):
        f = self.feat(fields)
        item = GeoItem(fields, f.geometry(), f.id())
        item.setValue('sources', sources)
        return (f, item)
