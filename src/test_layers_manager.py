import unittest

from qgis.core import *
from layers_manager import LayersManager
from main import StdOutLogAdapter

class QgsProj:

    def __init__(self, layers):
        self.layers = layers
        self._handlers = {}
        self.layersAdded = self

    def connect(self, fun):
        self._handlers['layers_added'] = fun
    
    def mapLayers(self):
        return self.layers

    def testAddLayer(self, name, lay):
        self.layers[name] = lay
        self._handlers['layers_added']([lay])

class DataProvider:

    def __init__(self, db):
        self._db = db
        self.features = []

    def database(self):
        return self._db

    def uri(self):
        return QgsDataSourceUri(self._db)

    def forceReload(self):
        pass
    
    def addFeatures(self, f):
        print(f)
        self.features.extend(f)
        f[0].setId(1234)
        return (True, f)

RECORDS_URI = 'dbname=\'test.sqlite\' table="AS_RECORDS" (geometry) sql='
    
class Layer:

    def __init__(self, valid=True, type=QgsMapLayer.VectorLayer, name='AS_records', db=RECORDS_URI):
        self._valid = valid
        self._type = type
        self._name = name
        self._dataProvider = DataProvider(db)
        self.selectionChanged = self
        self.handlers = {}

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
    
class LayersManagerTest(unittest.TestCase):

    def test_init_layer_is_loaded(self):
        qgsProj = QgsProj(layers={'as_records': Layer(), 'grid_50_m': Layer(name='grid_50_m')})
        man = LayersManager(qgsProj, StdOutLogAdapter(), lambda x: print(x))
        self.assertEqual(man.managed, {'AS_RECORDS', 'GRID_50_M'})

    def test_init_layer_selection_event_attached(self):
        qgsProj = QgsProj(layers={'as_records': Layer(), 'grid_50_m': Layer(name='grid_50_m')})
        feats = []
        man = LayersManager(qgsProj, StdOutLogAdapter(), lambda x: print(x))
        man.handlers['grid_selected'] = lambda x: feats.append(x)

        qgsProj.layers['grid_50_m'].handlers['selection_changed'](['test_selected_feature'],'b','c')

        self.assertEqual(feats, ['test_selected_feature'])    
        
    def test_init_layer_sources_loaded(self):
        src = []
        def layerFactory(s):
            src.append(s)
            return QgsVectorLayer(s, providerLib='test')
        qgsProj = QgsProj(layers={'as_records': Layer(), 'grid50': Layer(name='grid50')})
        man = LayersManager(qgsProj, StdOutLogAdapter(), layerFactory)

        self.assertTrue(isinstance(man.sources, QgsVectorLayer))
        self.assertEqual(src[1], RECORDS_URI
                         .replace('RECORDS','SOURCES')
                         .replace(' (geometry)', ''))

    def test_init_layer_squares_loaded(self):
        src = []
        def layerFactory(s):
            src.append(s)
            return QgsVectorLayer(s, providerLib='test')
        qgsProj = QgsProj(layers={'as_records': Layer(), 'grid50': Layer(name='grid50')})
        man = LayersManager(qgsProj, StdOutLogAdapter(), layerFactory)

        self.assertTrue(isinstance(man.sources, QgsVectorLayer))
        self.assertEqual(src[0], RECORDS_URI
                         .replace('RECORDS','SQUARES')
                         )

    def test_records_added_layer_loaded(self):
        qgsProj = QgsProj(layers={'grid_50_m': Layer(name='grid_50_m')})
        man = LayersManager(qgsProj, StdOutLogAdapter(), lambda x: print(x))

        qgsProj.testAddLayer('as_records', Layer())
        
        self.assertEqual(man.managed, {'AS_RECORDS', 'GRID_50_M'})

    def test_grid_added_layer_loaded(self):
        qgsProj = QgsProj(layers={'as_records': Layer()})
        man = LayersManager(qgsProj, StdOutLogAdapter(), lambda x: print(x))

        qgsProj.testAddLayer('Grid_50_m', Layer(name='Grid_50_m'))
        
        self.assertEqual(man.managed, {'AS_RECORDS', 'GRID_50_M'})

    def test_records_added_layer_sources_loaded(self):
        src = []
        def layerFactory(s):
            src.append(s)
            return QgsVectorLayer(s, providerLib='test')
        qgsProj = QgsProj(layers={'grid_50_m': Layer(name='grid_50_m')})
        man = LayersManager(qgsProj, StdOutLogAdapter(), layerFactory)

        qgsProj.testAddLayer('as_records', Layer())

        self.assertTrue(isinstance(man.sources, QgsVectorLayer))
        self.assertEqual(src[1], RECORDS_URI.replace('RECORDS','SOURCES').replace(' (geometry)', ''))

    def test_records_added_layer_squares_loaded(self):
        src = []
        def layerFactory(s):
            src.append(s)
            return QgsVectorLayer(s, providerLib='test')
        qgsProj = QgsProj(layers={'grid_50_m': Layer(name='grid_50_m')})
        man = LayersManager(qgsProj, StdOutLogAdapter(), layerFactory)

        qgsProj.testAddLayer('as_records', Layer())
        self.assertTrue(isinstance(man.sources, QgsVectorLayer))
        self.assertEqual(src[0], RECORDS_URI.replace('RECORDS','SQUARES'))

    def test_add_record(self):
        def layerFactory(s):
            return Layer(name=s)
        qgsProj = QgsProj(layers={'as_records': Layer(), 'grid_50_m': Layer(name='grid_50_m')})
        man = LayersManager(qgsProj, StdOutLogAdapter(), layerFactory)

        man.addRecord(self.feat(), self.feat())

        self.assertEqual(len(man.sources.dataProvider().features), 1)
        self.assertEqual(len(man.squares.dataProvider().features), 1)
        self.assertEqual(man.sources.dataProvider().features[0]['square'], 1234)

    def feat(self):
        f = QgsField('square', typeName='int')
        ff = QgsFields()
        ff.append(f)
        return QgsFeature(ff)
