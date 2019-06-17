# python [모듈 이름] [키워드] [가져올 페이지 숫자] [결과 파일명]
# 동아일보 크롤링
# 특정 키워드 포함
# 특정 날짜 이전 기사

# 정렬 - 최신순 / 범위 - 동아일보, 한국일보, 한겨레 / 기간 - 1개월
# http://news.donga.com/search?p=16&query=%EC%82%BC%EC%84%B1&check_news=1&more=1&sorting=1&search_date=3&v1=&v2=&range=3

from bs4 import BeautifulSoup
import urllib.request
from urllib.parse import quote
import urllib.error
from konlpy.tag import Kkma
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt

from PosNeg import stan

# 동아일보
DONGA_TARGET_URL_BEFORE_PAGE_NUM = "http://news.donga.com/search?p="
DONGA_TARGET_URL_BEFORE_KEWORD = '&query='
DONGA_TARGET_URL_REST = '&check_news=1&more=1&sorting=3&search_date=1&v1=&v2=&range=3'

# 한국일보
HANKOOK_TARGET_URL_BEFORE_PAGE_NUM = "http://search.hankookilbo.com/v2/?stype=&page="
HANKOOK_TARGET_URL_BEFORE_KEWORD = '&sword='
HANKOOK_TARGET_URL_REST = '&ssort=1'

# 한겨례
HANI_TARGET_URL_BEFORE_PAGE_NUM = "http://search.hani.co.kr/Search?pageseq="
HANI_TARGET_URL_BEFORE_KEWORD = '&keyword='
HANI_TARGET_URL_REST = '&command=query&media=news&sort=d&period=all'

class Analysis:
    def __init__(self):
        self.nouns = []
        self.positive_nouns = []
        self.negative_nouns = []
        self.sum = 0

    def get_link_from_news_title_donga(self, page_num, URL, keyword):
        for i in range(page_num):
            current_page_num = 1 + i * 15
            position = URL.index('=')
            URL_with_page_num = URL[: position + 1] + str(current_page_num) \
                                + URL[position + 1:]
            try:
                source_code_from_URL = urllib.request.urlopen(URL_with_page_num)
                soup = BeautifulSoup(source_code_from_URL, 'lxml', from_encoding='utf-8')
                for title in soup.find_all('p', 'tit'):
                    title_link = title.select('a')
                    article_URL = title_link[0]['href']
                    self.get_text(article_URL, keyword, 'div.article_txt')
            except urllib.error.URLError as e:
                print(source_code_from_URL, e)
            except ConnectionResetError as e:
                print(URL, e)


    # 기사 검색 페이지에서 기사 제목에 링크된 기사 본문 주소 받아오기 (한국일보)
    def get_link_from_news_title_hankook(self, page_num, URL, keyword):
        for i in range(page_num):
            current_page_num = i + 1
            position = URL.index('=')
            URL_with_page_num = URL[: position + 7] + str(current_page_num) \
                                + URL[position + 7:]
            try:
                source_code_from_URL = urllib.request.urlopen(URL_with_page_num)
                soup = BeautifulSoup(source_code_from_URL, 'lxml', from_encoding='utf-8')
                for title in soup.find_all('div', 'body'):
                    title_link = title.select('a')
                    if len(title_link) > 0:
                        article_URL = title_link[0]['href']
                        self.get_text(article_URL, keyword, 'div.article-story')
            except urllib.error.URLError as e:
                print(source_code_from_URL, e)
            except ConnectionResetError as e:
                print(URL, e)


    # 기사 검색 페이지에서 기사 제목에 링크된 기사 본문 주소 받아오기 (한겨례)
    def get_link_from_news_title_hani(self, page_num, URL, keyword):
        for i in range(page_num):
            current_page_num = i
            position = URL.index('=')
            URL_with_page_num = URL[: position + 1] + str(current_page_num) \
                                + URL[position + 1:]
            try:
                source_code_from_URL = urllib.request.urlopen(URL_with_page_num)
                soup = BeautifulSoup(source_code_from_URL, 'lxml', from_encoding='utf-8')
                ul = soup.find('ul', 'search-result-list')
                for title in soup.find_all('dt'):
                    title_link = title.select('a')
                    if len(title_link) > 0:
                        article_URL = title_link[0]['href']
                        self.get_text(article_URL, keyword, 'div.text')
            except urllib.error.URLError as e:
                print(URL_with_page_num, e)
            except ConnectionResetError as e:
                print(URL, e)

        # 기사 본문 내용 긁어오기 (위 함수 내부에서 기사 본문 주소 받아 사용되는 함수)
    def get_text(self, URL, keyword, div_class):
        try:
            source_code_from_url = urllib.request.urlopen(URL)
            soup = BeautifulSoup(source_code_from_url, 'lxml', from_encoding='utf-8')
            content_of_article = soup.select(div_class)
            for item in content_of_article:
                string_item = str(item.find_all(text=True))
                self.get_nouns(string_item, stan(string_item), keyword)
        except urllib.error.URLError as e:
            print(URL, e)
        except ConnectionResetError as e:
            print(URL, e)


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
        keyword = argv[1]
        page_num = (int)(argv[2])
        output_file_name = argv[3]

        # 동아일보
        target_URL = DONGA_TARGET_URL_BEFORE_PAGE_NUM + DONGA_TARGET_URL_BEFORE_KEWORD \
                     + quote(keyword) + DONGA_TARGET_URL_REST
        self.get_link_from_news_title_donga(page_num, target_URL, keyword)

        #한국일보
        target_URL = HANKOOK_TARGET_URL_BEFORE_PAGE_NUM + HANKOOK_TARGET_URL_BEFORE_KEWORD \
                     + quote(keyword) + HANKOOK_TARGET_URL_REST
        self.get_link_from_news_title_hankook(page_num, target_URL, keyword)

        # 한겨례
        target_URL = HANI_TARGET_URL_BEFORE_PAGE_NUM + HANI_TARGET_URL_BEFORE_KEWORD \
                     + quote(keyword) + HANI_TARGET_URL_REST
        self.get_link_from_news_title_hani(page_num, target_URL, keyword)

        # counter 생성
        pos_count = Counter(self.positive_nouns)
        neg_count = Counter(self.negative_nouns)
        count = Counter(self.nouns)

        # 빈도수 추출
        pos_tags = self.get_frequency(pos_count, 5)
        neg_tags = self.get_frequency(neg_count, 5)
        full_tags = self.get_frequency(count, 10)

        # 워드 클라우드 생성
        output_file_name = './imgs/' + output_file_name
        sum = self.make_wc(count, output_file_name)

        return {
            'sum': self.sum,
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