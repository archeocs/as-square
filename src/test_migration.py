import unittest
import sqlite3
import os
import migration

class MigrationTest(unittest.TestCase):

    def setUp(self):
        self.curDir = os.path.dirname(__file__)

    def createDb(self, stmts, version, dbName='test-db.sqlite'):
        dbPath = os.path.join(self.curDir, dbName)
        conn = sqlite3.connect(dbPath)
        conn.execute('CREATE TABLE AS_SETTINGS (SKEY TEXT, SVALUE TEXT)')
        conn.execute('INSERT INTO AS_SETTINGS VALUES(?, ?)', ('DB_VERSION', str(version)))
        for s in stmts:
            conn.execute(s)
        conn.commit()
        conn.close()
        return dbPath

    def createFile(self, name, lines):
        path = os.path.join(self.curDir, name)
        with open(path, 'w') as script:
            for l in lines:
                script.write(l)
                script.write('\n')
        return path

    def test_checkDb_database_up_to_date(self):
        method = 'test_checkDb_database_up_to_date';
        dbName = '{}.sqlite'.format(method)
        scriptName = '{}.sql'.format(method)
        dbPath = self.createDb(['CREATE TABLE T(X TEXT)'], 2,
                      dbName)
        scriptPath = self.createFile(scriptName,
                        ['ALTER TABLE T ADD COLUMN Y TEXT',
                         '-- ver: 2'])

        result = migration.checkDb(dbPath, scriptPath)
        self.assertEqual(result, (2, 2))

    def test_checkDb_database_not_up_to_date(self):
        method = 'test_checkDb_database_not_up_to_date';
        dbName = '{}.sqlite'.format(method)
        scriptName = '{}.sql'.format(method)
        dbPath = self.createDb(['CREATE TABLE T(X TEXT)'], 1,
                      dbName)
        scriptPath = self.createFile(scriptName,
                        ['ALTER TABLE T ADD COLUMN Y TEXT',
                         '-- ver: 2'])
        result = migration.checkDb(dbPath,
                                   scriptPath)
        self.assertEqual(result, (1, 2))

    def test_migrateDb_database_up_to_date(self):
        method = 'test_migrateDb_database_up_to_date';
        dbName = '{}.sqlite'.format(method)
        scriptName = '{}.sql'.format(method)
        dbPath = self.createDb(['CREATE TABLE T(X TEXT)'], 2,
                      dbName)
        scriptPath = self.createFile(scriptName,
                        ['ALTER TABLE T ADD COLUMN Y TEXT',
                         '-- ver: 2'])
        result = migration.migrateDb(dbPath,
                                   scriptPath)
        self.assertEqual(result, (True, None, None))

    
    def test_migrateDb_database_not_up_to_date(self):
        method = 'test_migrateDb_database_not_up_to_date';
        dbName = '{}.sqlite'.format(method)
        scriptName = '{}.sql'.format(method)
        dbPath = self.createDb(['CREATE TABLE T(X TEXT)'], 1,
                      dbName)
        scriptPath = self.createFile(scriptName,
                        ['ALTER TABLE T ADD COLUMN Y TEXT',
                         '-- ver: 2'])
        result = migration.migrateDb(dbPath,
                                   scriptPath)
        self.assertEqual(result, (True, 2, None))

    def removeDb(self, dbName='test-db.sqlite'):
        dbPath = os.path.join(self.curDir, dbName)
        os.remove(dbPath)
