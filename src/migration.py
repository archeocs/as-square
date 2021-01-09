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

def checkVersion(dbPath, last):
    db = QSqlDatabase.addDatabase('QSPATIALITE')
    db.setDatabaseName(dbPath)
    db.open()

    dbver = selectQuery(db,
                        "SELECT * FROM as_settings WHERE SKEY='DB_VERSION'")
    db.close()
    print(dbver)
    if dbver[0]:
        row = dbver[0][0]
        saved = row.get('SVALUE', None) or row.get('svalue', None)
        return int(saved) - int(last)
    else:
        print(dbver[1].text())
    return -1

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
            elif row.endswith(';'):
                nextStmt += ' ' + row[:-1]
                nextVer.append(nextStmt)
                nextStmt = ''
            else:
                nextStmt += ' ' + row
        print(versions, len(versions))
        return versions

def applyVersion(dbPath, stmts, num):
    db = QSqlDatabase.addDatabase('QSPATIALITE')
    db.setDatabaseName(dbPath)
    db.open()
    for s in stmts:
        result = updateQuery(db, s)
        if not result[0]:
            print('Migration failure on version', num, result[1].databaseText(), result[1].text())
            db.rollback()
            db.close()
            return
    ver = updateQuery(db, "UPDATE AS_SETTINGS SET SVALUE='{}' WHERE SKEY='{}'".format(num, 'DB_VERSION'))
    print('VER ', ver[0], ver[1].databaseText())
    print(db.commit())
    print('updated to version', num)
    db.close()

if __name__ == '__main__':
    db = '/home/milosz/git/as-square/empty-db.sqlite'
    script = readScript('/home/milosz/git/as-square/assquare-migration-db.sql')
    verDiff = checkVersion(db, len(script) - 1)
    start = len(script) - verDiff
    if verDiff < 0:
        for (vi, v) in enumerate(script):
            applyVersion(db, v, vi)
    else:
        print('DB up to date')
    print('OK')
