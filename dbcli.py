def create_database_if_exists(db, cursor):
    cursor.execute("""
    CREATE DATABASE IF NOT EXISTS 'decouvrir';
    """)
    db.commit()

'''
 Input:
    - existing database connection -> cursor
    - table name to check -> table

 Returns:
     Boolean
'''
def check_if_table_created(cursor, table):
    cursor.execute("""
    SELECT COUNT(*)
    FROM information_schema.tables
    WHERE table_name='{0}';
    """).format(table)
    if (cursor.fetchone()[0] == 1):
        return True
    return False

def create_table_if_exists(db, cursor):
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS `devices` (
        `id` INT NOT NULL AUTO_INCREMENT,
        `ip` VARCHAR(255),
        `hostname` VARCHAR(255),
        `first_seen` TIMESTAMP DEFAULT '1970-01-01 00:00:01',
        `updated_at` TIMESTAMP ON UPDATE CURRENT_TIMESTAMP DEFAULT '1970-01-01 00:00:01',
        `last_status` VARCHAR(255),
        KEY `ip` (`ip`) USING BTREE,
        KEY `hostname` (`hostname`) USING BTREE,
        PRIMARY KEY (`id`)
    ) ENGINE=InnoDB;
    """)
    db.commit()

def insert_into_table(db, cursor, query):
    try:
        cursor.execute(query)
        db.commit()
    except Exception as e:
        return e

def check_if_exists_with_id(cursor, id):
    try:
        result = cursor.execute("""
        SELECT COUNT(*) FROM devices WHERE id='{0}'
        """).format(id)
        if (result.fetchone()[0] == 1):
            return result
        return False
    except Exception as e:
        return e

def check_if_exists_with_ip(cursor, ip):
    try:
        result = cursor.execute("""
        SELECT COUNT(*) FROM devices WHERE ip='{0}'
        """).format(ip)
        if (result.fetchone()[0] == 1):
            return result
        return False
    except Exception as e:
        return e

def check_if_exists_with_hostname(cursor, hostname):
    try:
        result = cursor.execute("""
        SELECT COUNT(*) FROM devices WHERE ip='{0}'
        """).format(hostname)
        if (result.fetchone()[0] == 1):
            return result
        return False
    except Exception as e:
        return e