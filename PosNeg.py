# -*- coding: utf-8 -*-

from konlpy.tag import Okt
from konlpy.utils import pprint
import codecs
import csv

def mkNoun(str):
    # src = codecs.open(filename, 'r', encoding='utf8').read()
    okt = Okt()
    # print(src)
    # print('-' * 20)

    # malist = okt.nouns(src)

    malist = okt.nouns(str)
    #pprint(malist)

    return malist


def mkDic():
    dic = {}
    # f = open('./polarity.csv', 'r')
    f = open('./polarity.csv', 'r', encoding='UTF8')
    rdr = csv.reader(f)

    first = True
    for line in rdr:
        if first:
            first = False
            continue
        if not line[0].split('/')[0] in dic:
            dic[line[0].split('/')[0]] = [line[3], line[6]]
            # print(dic[line[0].decode('utf-8').split('/')[0]])
    f.close()

    return dic

def countPN(malist, dic):
    pos = 0
    neg = 0
    sum = len(malist)
    for m in malist:
        if m[0] in dic:
            pos = pos + (float)(dic[m[0]][1])
            neg = neg + (float)(dic[m[0]][0])
            # if dic[m[0]][1] == '1':
            #     print(m[0])

    return pos / sum, neg / sum

def stan(filename):
    malist = mkNoun(filename)

    dic = mkDic()

    pos, neg = countPN(malist, dic)


    if pos > 0.35:
        return 1    # 1: 긍정
    elif neg > 0.30:
        return -1   # -1: 부정
    else:
        return 0

if __name__ == '__main__':
    result = stan('./src_neg.txt')
    if result == 1:
        print('긍정')
    elif result == -1:
        print('부정')