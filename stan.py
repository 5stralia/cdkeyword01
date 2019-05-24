# -*- coding: utf-8 -*-

from konlpy.tag import Okt
import codecs
import csv

def mkNoun(filename):
    src = codecs.open(filename, 'r', encoding='utf8').read()
    okt = Okt()
    print(src)
    print('-' * 20)

    malist = okt.pos(src, norm=True, stem=True)

    for tuple in malist[:]:
        if tuple[1] != 'Noun':
          malist.remove(tuple)

    return malist


def mkDic():
    dic = {}
    f = open('./polarity.csv', 'r')
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

    if (pos > neg):
        return 1    # 1: 긍정
    else:
        return -1   # -1: 부정

if __name__ == '__main__':
    result = stan('./src_pos.txt')
    if result == 1:
        print('긍정')
    elif result == -1:
        print('부정')
