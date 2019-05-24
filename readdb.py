import pymysql

def searchP():
    conn = pymysql.connect(
        host='13.209.68.220',
        user='cdkeyword',
        password='password',
        db='cdkeyword')
    try:
        curs = conn.cursor()
        sql = """
                        SELECT keyword, COUNT(*)
                        FROM Search
                        GROUP BY keyword
                        ORDER BY COUNT(*) DESC
                        LIMIT 10;"""
        curs.execute(sql)

        return curs.fetchall()
    finally:
        conn.close()

def searchDb(name):
    conn = pymysql.connect(
        host='13.209.68.220',
        user='cdkeyword',
        password='password',
        db='cdkeyword')
    try:
        curs = conn.cursor()
        sql = """
                    INSERT INTO Search(keyword) VALUE(%s)
                """
        curs.execute(sql, name)
        conn.commit()

        sql = """
                    SELECT Keywords.rank, Keywords.name, Keywords.count, POS.name, NEG.name
                    FROM Keywords
                    LEFT OUTER JOIN POS ON Keywords.keywords_pk = POS.POS_pk AND Keywords.rank = POS.rank
                    LEFT OUTER JOIN NEG ON Keywords.keywords_pk = NEG.NEG_pk AND Keywords.rank = NEG.rank,
                    Name
                    WHERE Name.name = %s AND Keywords.keywords_pk = Name.pk
                    ORDER BY Keywords.rank"""
        curs.execute(sql, name)

        return curs.fetchall()
    finally:
        conn.close()

