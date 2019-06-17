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
        rows = None
        try:
            sql = """
                            SELECT keyword, COUNT(*)
                            FROM Search
                            GROUP BY keyword
                            ORDER BY COUNT(*) DESC
                            LIMIT 10"""
            self.curs.execute(sql)
            rows = self.curs.fetchall()

        except pymysql.err.DatabaseError as e:
            print("searchP", e)
        finally:
            self.conn.close()

        return rows

    def searchDb(self, name):
        rows = None
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
            rows = self.curs.fetchall()


        except pymysql.err.DatabaseError as e:
            print("searchDb", e)
        finally:
            self.conn.close()

        return rows, sumOfKeyword

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
        finally:
            self.conn.close()

    def isIn(self, name):
        try:
            sql = "SELECT * FROM Name WHERE name = %s"
            self.curs.execute(sql, name)
            rows = self.curs.fetchall()
            if not rows:
                print('start crawling', name)
                try:
                    threading.Thread(target=self.threadDb, args=(name, )).start()
                except threading.ThreadError as e:
                    print(e)
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
        print(name, 'keywords:: ', keywords)
        print('end crawling', name)
        self.inDb(name, keywords, fk)
        print('input db', name)