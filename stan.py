# -*- coding: utf-8 -*-

from konlpy.tag import Okt
import codecs
import csv

def mkNoun(filename):
    src = codecs.open(filename, 'r', encoding='utf8').read()
    okt = Okt()

    malist = okt.nouns(src)

    return malist

def mkDic():
    dic = {}
    f = open('./polarity.csv', 'r')
    rdr = csv.reader(f)

    for line in rdr[1:]:
        if not line[0].split('/')[0] in dic:
            dic[line[0].split('/')[0]] = [line[3], line[6]]
    f.close()

    return dic

def countPN(malist, dic):
    pos = 0
    neg = 0

    for m in malist:
        if m[0] in dic:
            pos = pos + (float)(dic[m[0]][1])
            neg = neg + (float)(dic[m[0]][0])

    sumPN = neg + pos
    return pos / sumPN, neg / sumPN

def stan(filename):
    malist = mkNoun(filename)

    dic = mkDic()

    pos, neg = countPN(malist, dic)

    if pos > 0.35:
        return 1    # 1: 긍정
    elif neg > 0.35:
        return -1   # -1: 부정
    else:
        return 0    # 0: 중립