# Copyright (C) Miłosz Pigłas <milosz@archeocs.com>
#
# Licensed under the European Union Public Licence

from PyQt5.QtSql import *

def selectQuery(db, query, params={}):
    rows = []
    print('query', query)
    q = QSqlQuery(db)
    for (k, v) in params.items():
        print('bind ', k, v)
        q.bindValue(':'+k, v)
    q.exec_(query)
    while q.next():
        row = {}
        rec = q.record()
        fc = rec.count()
        for x in range(fc):
            field = rec.field(x)
            row[field.name()] = field.value()
        rows.append(row)
    print('finish')
    return rows, q.lastError()

def updateQuery(db, query, params={}):
    print('query', query)
    q = QSqlQuery(db)
    for (k, v) in params.items():
        print('bind ', k, v)
        q.bindValue(':'+k, v)
    return (q.exec_(query), q.lastError())

def checkVersion(db, last):
    db.open()
    dbver = selectQuery(db,
                        "SELECT * FROM as_settings WHERE SKEY='DB_VERSION'")
    db.close()
    print(dbver)
    if dbver[0]:
        row = dbver[0][0]
        saved = row.get('SVALUE', None) or row.get('svalue', None)
        return (int(saved), int(saved) - int(last))
    else:
        print(dbver[1].databaseText())
        return None
    return (int(saved), -1)

def readScript(scriptPath):
    with open(scriptPath) as sf:
        versions = [(), ()]
        nextVer = []
        nextStmt = ''
        for r in sf.readlines():
            row = r.strip()
            if row == '':
                continue
            print(row)
            if row.startswith('-- ver:'):
                versions.append(nextVer)
                nextVer = []
            elif row.startswith('--'):
                continue
            elif row.endswith(';'):
                nextStmt += ' ' + row[:-1]
                nextVer.append(nextStmt)
                nextStmt = ''
            else:
                nextStmt += ' ' + row
        print(versions, len(versions))
        return versions

def applyVersion(db, stmts, num):
    db.open()
    for s in stmts:
        result = updateQuery(db, s)
        if not result[0]:
            print('Migration failure on version', num, result[1].databaseText(), result[1].text())
            db.rollback()
            db.close()
            return False
    ver = updateQuery(db, "UPDATE AS_SETTINGS SET SVALUE='{}' WHERE SKEY='{}'".format(num, 'DB_VERSION'))
    print(db.commit())
    print('updated to version', num)
    db.close()
    return True

def checkDb(dbPath, scriptPath):
    script = readScript(scriptPath)
    db = QSqlDatabase.addDatabase('QSPATIALITE')
    db.setDatabaseName(dbPath)
    check = checkVersion(db, len(script) - 1)
    db.close()
    if check is None:
        return None
    return (check[0], len(script) - 1)

def migrateDb(dbPath, scriptPath):
    script = readScript(scriptPath)
    db = QSqlDatabase.addDatabase('QSPATIALITE')
    db.setDatabaseName(dbPath)
    check = checkVersion(db, len(script) - 1)
    if check is None:
        return (False, None, 'Checking version failed')
    start = len(script) + check[1]
    print('start', start)
    if check[1] < 0:
        for (vi, v) in enumerate(script):
            if vi >= start and not applyVersion(db, v, vi):
                return (False, None, 'Migration to version ' + str(vi) + ' failed')
    else:
        return (True, None, None)
    return (True, len(script) -1, None)

if __name__ == '__main__':
    import sys
    result = migrateDb(sys.argv[0], sys.argv[1])
    if not result[0]:
        print('Migration failed ', result[2])
    elif result[1] is None:
        print('Database already up to date')
    else:
        print('Databae migrated to version', result[1])
