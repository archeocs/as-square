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
            print('row', row)
    print('finish')
    return rows, q.lastError()

def checkVersion(dbPath):
    db = QSqlDatabase.addDatabase('QSPATIALITE')
    db.setDatabaseName(dbPath)
    db.open()

    dbver = selectQuery(db,
                        'SELECT * FROM as_settings WHERE skey = :k',
                        {'k': 'DB_VERSION'})
    dv2 = selectQuery(db, 'select * from as_settings')
    db.close()
    return dbver, dv2
