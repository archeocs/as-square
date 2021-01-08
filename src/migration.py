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


if __name__ == '__main__':
    script = readScript('/home/milosz/git/as-square/assquare-migration-db.sql')
    print(checkVersion('/home/milosz/git/as-square/empty-db.sqlite', len(script) - 1))
