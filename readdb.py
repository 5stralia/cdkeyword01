import pymysql
import threading

from AnalysisNewsKewords import Analysis

class DB:

    def __init__(self):
        self.conn = pymysql.connect(
            host='13.209.68.220',
            user='cdkeyword',
            password='password',
            db='cdkeyword')
        self.curs = self.conn.cursor()

    def searchP(self):
        try:
            sql = """
                            SELECT keyword, COUNT(*)
                            FROM Search
                            GROUP BY keyword
                            ORDER BY COUNT(*) DESC
                            LIMIT 10"""
            self.curs.execute(sql)

        except pymysql.err.DatabaseError as e:
            print("searchP", e)

        return self.curs.fetchall()

    def searchDb(self, name):
        try:
            sql = """
                        INSERT INTO Search(keyword) VALUE(%s)
                    """
            self.curs.execute(sql, name)
            self.conn.commit()

            sql = "SELECT sum FROM Name WHERE name = %s"
            self.curs.execute(sql, name)
            rows = self.curs.fetchall()
            sumOfKeyword = 0
            for r in rows:
                sumOfKeyword = (int)(r[0])

            sql = """
                        SELECT Keywords.rank, Keywords.name, Keywords.count, POS.name, NEG.name
                        FROM Keywords
                        LEFT OUTER JOIN POS ON Keywords.keywords_pk = POS.POS_pk AND Keywords.rank = POS.rank
                        LEFT OUTER JOIN NEG ON Keywords.keywords_pk = NEG.NEG_pk AND Keywords.rank = NEG.rank,
                        Name
                        WHERE Name.name = %s AND Keywords.keywords_pk = Name.pk
                        ORDER BY Keywords.rank"""
            self.curs.execute(sql, name)


        except pymysql.err.DatabaseError as e:
            print("searchDb", e)

        return self.curs.fetchall(), sumOfKeyword

    def insertName(self, name):
        try:
            sql = "INSERT INTO Name(name, sum) VALUE(%s, 0)"
            self.curs.execute(sql, (name, ))
            self.conn.commit()

            sql = "SELECT LAST_INSERT_ID()"
            self.curs.execute(sql)
            rows = self.curs.fetchall()
            fk = -1
            for r in rows:
                fk = r[0]

            return fk
        except pymysql.err.DatabaseError as e:
            print("error insertName", e)

    def inDb(self, name, keywords, fk):
        try:
            sql = "UPDATE Name SET sum = %s WHERE name=%s"
            self.curs.execute(sql, (keywords['sum'], name))
            self.conn.commit()

            rank = 1
            for item in keywords['full']:
                sql = """
                    INSERT INTO Keywords(rank, name, keywords_pk, count)
                    VALUE(%s, %s, %s, %s)
                """
                rank = rank + 1
                print('data', (rank, item['tag'], fk, item['count'], ))
                self.curs.execute(sql, (rank, item['tag'], fk, item['count'], ))

            rank = 1
            for item in keywords['pos']:
                sql = """
                        INSERT INTO POS(rank, name, POS_pk)
                        VALUE(%s, %s, %s)
                        """
                rank = rank + 1
                self.curs.execute(sql, (rank, item['tag'], fk, ))


            rank = 1
            for item in keywords['neg']:
                sql = """
                        INSERT INTO NEG(rank, name, NEG_pk)
                        VALUE(%s, %s, %s)
                        """
                rank = rank + 1
                self.curs.execute(sql, (rank, item['tag'], fk, ))

            self.conn.commit()


        except pymysql.err.DatabaseError as e:
            print("error inDb", e)

    def isIn(self, name):
        try:
            sql = "SELECT * FROM Name WHERE name = %s"
            self.curs.execute(sql, name)
            rows = self.curs.fetchall()
            if not rows:
                print('start crawling', name)
                threading.Thread(target=self.threadDb, args=(name, )).start()
                return False
            else:
                print('exist name', name)
                return True

        except pymysql.DatabaseError as e:
            print('isIn', e)
        except threading.ThreadError as e:
            print('isIn', e)

    def threadDb(self, name):
        print('thread start', name)
        fk = self.insertName(name)
        analysis = Analysis()
        keywords = analysis.runOnWeb(name)
        print('end crawling', name)
        self.inDb(name, keywords, fk)
        print('input db', name)

if __name__ == '__main__':
    db = DB()

    sum = 30
    full = [
        {'tag': 'tag1', 'count': 1},
        {'tag': 'tag2', 'count': 2},
        {'tag': 'tag3', 'count': 3},
        {'tag': 'tag4', 'count': 4},
        {'tag': 'tag5', 'count': 5},
        {'tag': 'tag6', 'count': 6},
        {'tag': 'tag7', 'count': 7},
        {'tag': 'tag8', 'count': 8},
        {'tag': 'tag9', 'count': 9},
        {'tag': 'tag10', 'count': 10},
    ]
    pos = [
        {'tag': 'tag1', 'count': 1},
        {'tag': 'tag2', 'count': 2},
        {'tag': 'tag3', 'count': 3},
        {'tag': 'tag4', 'count': 4},
        {'tag': 'tag5', 'count': 5},
    ]
    neg = [
        {'tag': 'tag1', 'count': 1},
        {'tag': 'tag2', 'count': 2},
        {'tag': 'tag3', 'count': 3},
        {'tag': 'tag4', 'count': 4},
        {'tag': 'tag5', 'count': 5},
    ]

    data = {'sum': sum,
            'full': full,
            'pos': pos,
            'neg': neg}

    test = 'test5'
    db.insertName(test)
    db.inDb(test, data)
