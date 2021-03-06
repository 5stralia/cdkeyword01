# python [모듈 이름] [키워드] [가져올 페이지 숫자] [결과 파일명]
# 동아일보 크롤링
# 특정 키워드 포함
# 특정 날짜 이전 기사

# 정렬 - 최신순 / 범위 - 동아일보 / 기간 - 1개월
# http://news.donga.com/search?p=16&query=%EC%82%BC%EC%84%B1&check_news=1&more=1&sorting=1&search_date=3&v1=&v2=&range=3

from bs4 import BeautifulSoup
import urllib.request
from urllib.parse import quote
from PosNeg import stan
import sys
from konlpy.tag import Kkma
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import time

TARGET_URL_BEFORE_PAGE_NUM = "http://news.donga.com/search?p="
TARGET_URL_BEFORE_KEWORD = '&query='
TARGET_URL_REST = '&check_news=1&more=1&sorting=3&search_date=1&v1=&v2=&range=3'

class Analysis:
    def __init__(self):
        self.nouns = []
        self.positive_nouns = []
        self.negative_nouns = []
        self.sum = 0

    # 기사 검색 페이지에서 기사 제목에 링크된 기사 본문 주소 받아오기
    def get_link_from_news_title(self, page_num, URL, keyword):
        for i in range(page_num):
            current_page_num = 1 + i * 15
            position = URL.index('=')
            URL_with_page_num = URL[: position + 1] + str(current_page_num) \
                                + URL[position + 1:]
            source_code_from_URL = urllib.request.urlopen(URL_with_page_num)
            soup = BeautifulSoup(source_code_from_URL, 'lxml', from_encoding='utf-8')
            for title in soup.find_all('p', 'tit'):
                title_link = title.select('a')
                article_URL = title_link[0]['href']
                self.get_text(article_URL, keyword)

        # 기사 본문 내용 긁어오기 (위 함수 내부에서 기사 본문 주소 받아 사용되는 함수)
    def get_text(self, URL, keyword):
        source_code_from_url = urllib.request.urlopen(URL)
        soup = BeautifulSoup(source_code_from_url, 'lxml', from_encoding='utf-8')
        content_of_article = soup.select('div.article_txt')
        for item in content_of_article:
            string_item = str(item.find_all(text=True))
            self.get_nouns(string_item, stan(string_item), keyword)

    # 명사 찾아서 긍정, 부정, 전체에 넣기
    def get_nouns(self, text, isPositive, keyword):
        spliter = Kkma()
        isnouns = ['NNG', 'NNP']
        tags = spliter.pos(text)
        # 긍정일 때
        if isPositive == 1:
            for i in tags:
                if i[1] in isnouns and len(i[0]) > 1 and i[0] not in keyword:
                    self.nouns.append(i[0])
                    self.positive_nouns.append(i[0])
        # 부정일 때
        elif isPositive == -1:
            for i in tags:
                if i[1] in isnouns and len(i[0]) > 1 and i[0] not in keyword:
                    self.nouns.append(i[0])
                    self.negative_nouns.append(i[0])
        else:
            for i in tags:
                if i[1] in isnouns and len(i[0]) > 1 and i[0] not in keyword:
                    self.nouns.append(i[0])

    # counter로부터 빈도수 추출
    def get_frequency(self, count, ntags):
        return_list = []
        for n, c in count.most_common(ntags):
            temp = {'tag': n, 'count': c}
            return_list.append(temp)
        return return_list

    # 워드 클라우드 생성
    def make_wc(self, count, output_file):
        # 상위 n건 추출
        most = count.most_common(100)
        # 딕션너리 구성
        tags = {}
        for n, c in most:
            tags[n] = c
            self.sum = self.sum + c
        # 워드클라우드 생성
        wc = WordCloud(font_path='C:\Windows\Fonts\H2HDRM.ttf', background_color='white', width=1200, height=800,
                       scale=2.0,
                       max_font_size=250)
        gen = wc.generate_from_frequencies(tags)
        plt.figure()
        plt.axis("off")
        plt.imshow(gen, interpolation='bilinear')
        wc.to_file(output_file + '.png')
        plt.close()

        return sum

    def main(self, argv):
        start_time = time.time()

        keyword = argv[1]
        page_num = (int)(argv[2])
        output_file_name = argv[3]

        target_URL = TARGET_URL_BEFORE_PAGE_NUM + TARGET_URL_BEFORE_KEWORD \
                     + quote(keyword) + TARGET_URL_REST
        self.get_link_from_news_title(page_num, target_URL, keyword)

        # counter 생성
        pos_count = Counter(self.positive_nouns)
        neg_count = Counter(self.negative_nouns)
        count = Counter(self.nouns)

        # 빈도수 추출
        pos_tags = get_frequency(pos_count, 5)
        neg_tags = get_frequency(neg_count, 5)
        full_tags = get_frequency(count, 10)

        # 워드 클라우드 생성
        output_file_name = './imgs/' + output_file_name
        sum = make_wc(count, output_file_name)

        # print("전체개수")
        # print(sum)
        # print("<Positive>")
        # print(pos_tags)
        # print("<Negative>")
        # print(neg_tags)
        # print("<Entire>")
        # print(full_tags)
        #
        # print((str)(time.time() - start_time) + " seconds")

        return {
            'sum': sum,
            'full': full_tags,
            'pos': pos_tags,
            'neg': neg_tags
        }

    def runOnWeb(self, query):
        arg = [None]
        arg.append(query)
        arg.append('10')
        arg.append(query)
        return self.main(arg)


# 기사 검색 페이지에서 기사 제목에 링크된 기사 본문 주소 받아오기
def get_link_from_news_title(page_num, URL, keyword):
    for i in range(page_num):
        positive_nouns = []
        negative_nouns = []
        nouns = []

        current_page_num = 1 + i * 15
        position = URL.index('=')
        URL_with_page_num = URL[: position + 1] + str(current_page_num) \
                            + URL[position + 1:]
        source_code_from_URL = urllib.request.urlopen(URL_with_page_num)
        soup = BeautifulSoup(source_code_from_URL, 'lxml', from_encoding='utf-8')
        for title in soup.find_all('p', 'tit'):
            title_link = title.select('a')
            article_URL = title_link[0]['href']
            full, pos, neg = get_text(article_URL, keyword)
            nouns.extend(full)
            positive_nouns.extend(pos)
            negative_nouns.extend(neg)

        return nouns, positive_nouns, negative_nouns

# 기사 본문 내용 긁어오기 (위 함수 내부에서 기사 본문 주소 받아 사용되는 함수)
def get_text(URL, keyword):
    positive_nouns = []
    negative_nouns = []
    nouns = []

    source_code_from_url = urllib.request.urlopen(URL)
    soup = BeautifulSoup(source_code_from_url, 'lxml', from_encoding='utf-8')
    content_of_article = soup.select('div.article_txt')
    for item in content_of_article:
        string_item = str(item.find_all(text=True))
        full, pos, neg = get_nouns(string_item, stan(string_item), keyword)
        nouns.extend(full)
        positive_nouns.extend(pos)
        negative_nouns.extend(neg)

    return nouns, positive_nouns, negative_nouns


# 명사 찾아서 긍정, 부정, 전체에 넣기
def get_nouns(text, isPositive, keyword):
    positive_nouns = []
    negative_nouns = []
    nouns = []

    spliter = Kkma()
    isnouns = ['NNG', 'NNP']
    tags = spliter.pos(text)
    # 긍정일 때
    if isPositive == 1:
        for i in tags:
            if i[1] in isnouns and len(i[0]) > 1 and i[0] not in keyword:
                nouns.append(i[0])
                positive_nouns.append(i[0])
    # 부정일 때
    elif isPositive == -1:
        for i in tags:
            if i[1] in isnouns and len(i[0]) > 1 and i[0] not in keyword:
                nouns.append(i[0])
                negative_nouns.append(i[0])
    else:
        for i in tags:
            if i[1] in isnouns and len(i[0]) > 1 and i[0] not in keyword:
                nouns.append(i[0])

    return nouns, positive_nouns, negative_nouns

# counter로부터 빈도수 추출
def get_frequency(count, ntags):
    return_list = []
    for n, c in count.most_common(ntags):
        temp = {'tag': n, 'count': c}
        return_list.append(temp)
    return return_list

# 워드 클라우드 생성
def make_wc(count, output_file):
    sum = 0

    # 상위 n건 추출
    most = count.most_common(100)
    # 딕션너리 구성
    tags = {}
    for n, c in most:
        tags[n] = c
        sum = sum + c
    # 워드클라우드 생성
    wc = WordCloud(font_path='C:\Windows\Fonts\H2HDRM.ttf', background_color='white', width=1200, height=800, scale=2.0,
                   max_font_size=250)
    gen = wc.generate_from_frequencies(tags)
    plt.figure()
    plt.axis("off")
    plt.imshow(gen, interpolation='bilinear')
    wc.to_file(output_file+'.png')
    plt.close()

    return sum

def main(argv):
    start_time = time.time()

    keyword = argv[1]
    page_num = (int)(argv[2])
    output_file_name = argv[3]

    target_URL = TARGET_URL_BEFORE_PAGE_NUM + TARGET_URL_BEFORE_KEWORD \
                 + quote(keyword) + TARGET_URL_REST
    nouns, positive_nouns, negative_nouns = get_link_from_news_title(page_num, target_URL, keyword)

    # counter 생성
    pos_count = Counter(positive_nouns)
    neg_count = Counter(negative_nouns)
    count = Counter(nouns)

    # 빈도수 추출
    pos_tags = get_frequency(pos_count, 5)
    neg_tags = get_frequency(neg_count, 5)
    full_tags = get_frequency(count, 10)

    # 워드 클라우드 생성
    output_file_name = './imgs/' + output_file_name
    sum = make_wc(count, output_file_name)


    # print("전체개수")
    # print(sum)
    # print("<Positive>")
    # print(pos_tags)
    # print("<Negative>")
    # print(neg_tags)
    # print("<Entire>")
    # print(full_tags)
    #
    # print((str)(time.time() - start_time) + " seconds")

    return {
        'sum': sum,
        'full': full_tags,
        'pos': pos_tags,
        'neg': neg_tags
    }

def runOnWeb(query):
    arg = [None]
    arg.append(query)
    arg.append('10')
    arg.append(query)
    return main(arg)

if __name__ == '__main__':
    result = runOnWeb('삼성')
    print(result)