# -*- coding= utf-8 -*-

from flask import Flask
from flask_restful import Resource, Api
from flask_cors import CORS
from flask import send_file

from readdb import DB
from AnalysisNewsKewords import runOnWeb

app = Flask(__name__)
api = Api(app)
CORS(app)

db = DB()

class SearchPopular(Resource):
    def get(self):
        keywords = []
        rows = db.searchP()
        for r in rows:
            keywords.append({
                'keyword': r[0],
                'count': r[1]})
        return {'status': 'success',
                'keywords': keywords}

class SearchKeywords(Resource):
    def get(self, name):
        rows, sumOfKeyword = db.searchDb(name)

        if not rows:
            # todo : 저장된 자료가 없으니 크롤링 시작시키기
            db.isIn(name=name)
            return {'get': 'fail'}

        # todo : 너무 오래된 자료일 때 크롤링 시작시키기

        keywords = []
        pos = []
        neg = []

        for r in rows:
            if r[1]:
                keywords.append({'name': r[1], 'count': r[2]})
            if r[3]:
                pos.append(r[3])
            if r[4]:
                neg.append(r[4])

        return {'get': 'success',
                'sum': sumOfKeyword,
                'keywords':
                    {'items': keywords,
                     'size': len(keywords)},
                'pos':
                    {'items': pos,
                     'size': len(pos)},
                'neg':
                    {'items': neg,
                     'size': len(neg)}
                }

class SearchImg(Resource):
    def get(self, filename):
        filename = './imgs/' + filename
        return send_file(filename, mimetype='image/png')

api.add_resource(SearchPopular, '/popular')
api.add_resource(SearchKeywords, '/search/<string:name>')
api.add_resource(SearchImg, '/searchimg/<string:filename>')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
    # app.run(debug=True)
