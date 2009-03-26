import os, sqlite3
from higgins.core.upgradedb.logger import logger

def check_version(dbpath):
    from higgins.core.models import DB_VERSION
    # if db doesn't exist, then create a new one
    if not os.access(dbpath, os.F_OK):
        version = 0
    else:
        version = None
    db = sqlite3.connect(dbpath)
    if version == None:
        try:
            cursor = db.cursor()
            cursor.execute("SELECT MAX(version) FROM dbinfo")
            version = int(cursor.fetchone()[0])
            if version > DB_VERSION:
                raise Exception("database version %i is newer than this version of Higgins!" % version)
        except Exception, e:
            logger.log_fatal("couldn't get the current db version: %s" % e)
            raise Exception("database version check failed")
    logger.log_debug("database version is %i" % version)
    while version < DB_VERSION:
        try:
            new_version = version + 1
            logger.log_debug("upgrading to version %i" % new_version)
            mod = __import__('to_%i' % new_version, globals(), locals(), 'higgins.core.upgradedb')
            mod.upgrade(db)
            cursor = db.cursor()
            cursor.execute("INSERT INTO dbinfo VALUES(%i, date('now'))" % new_version)
            db.commit()
            version = new_version
        except Exception, e:
            db.close()
            logger.log_fatal("failed to upgrade database: %s" % e)
            raise Exception("database version check failed")
    db.close()
