# 라이브러리 import
import os
import pandas as pd
import numpy as np
import math

# 셀레늄
from selenium.webdriver.common.alert import Alert
from selenium import webdriver  # 라이브러리(모듈) 가져오라
# pip install chromedriver_autoinstaller
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains as AC


# 정규표현식(regular expression) : 문자(알파벳,한글), 숫자, 특수기호 정제 및 추출
import re
from time import sleep
import time

# 워닝 무시
import warnings

warnings.filterwarnings('ignore')

from selenium.webdriver.common.by import By
import chromedriver_autoinstaller

# deque
from collections import deque

# parsing
import bs4
from bs4 import BeautifulSoup

# request
import requests

# 검색어 입력
search = '오아시스마켓'
# 크롬 옵션
options = webdriver.ChromeOptions()
# 크롬 윈도우 사이즈 조절
options.add_argument("--window-size=1920,1080")  # window-size -> 기본 : 1920,1080
chrome_path = chromedriver_autoinstaller.install()
driver = webdriver.Chrome(chrome_path, options=options)
driver.get("https://www.naver.com")
# -> 네이버 크롬 창이 뜬다.

# 네이버 검색어 입력 후 검색
element = driver.find_element("name", "query")
element.clear()  # 혹시 검색창에 존재하는 텍스트 제거
element.send_keys(search)  # 검색창에 검색어 전달
element.submit()  # 검색 클릭

# 뉴스 클릭
driver.find_element("link text", "뉴스").click()

# 옵션 클릭 후 '1년' 클릭
# find_elements로 리스트로 return후 인덱스로 element에 접근
driver.implicitly_wait(2)  # 2초 대기
option_ = driver.find_elements(By.XPATH, "//*[@id=\"snb\"]/div[1]/div/div[2]/a")[0].click()  # 옵션 클릭
year1_ = driver.find_elements(By.XPATH, "//*[@id=\"snb\"]/div[2]/ul/li[2]/div/div[1]/a[8]")  # 1년 후 클릭
driver.implicitly_wait(2)  # 2초 대기
driver.execute_script("arguments[0].click();", year1_[0])  ## JS_Executor로 script 실행


def find_naver_news():  # 현재 목록 페이지에서 네이버뉴스 하이퍼링크가 존재하는 <a> tag, class = 'info'를 찾습니다.
    """
        find_naver_news()
            ARGS:
                None
            Returns:
                각 네이버뉴스의 URL을 담고있는 Queue
    """
    current_url = driver.current_url  # 현재 페이지의 URL을 sting으로 변수에 할당합니다.
    response = requests.get(current_url)  # 요청을 받아옵니다. Response 객체가 response에 할당됩니다.
    soup = BeautifulSoup(response.text, "html.parser")  # 파싱 후 BS4객체를 soup에 할당합니다.
    temp = soup.find_all("a", class_="info")  # BS4객체에서 find_all 메소드를 통해서 <a> tag, class= 'info'에 접근합니다.
    # 하지만 진짜 원하는 calss = 'info' 말고 class = 'info press'도 함께 추출됩니다. 따라서 이를 걸러주는 코드가 필요합니다.
    temp2 = soup.find_all("a", class_="info press")  # class = 'info press'만 추출하는 함수
    info_class = deque()
    for _ in temp:
        if _ not in temp2:
            info_class.append(_['href'])
    return info_class  # 현재 페이지의 URL을 가져옵니다.


# 본문 추출 함수
def content(_url_=''):
    """
          content(url)
            ARGS:
                url = info_class[i] , info_class deque에 담긴 각 요소를 인자로 받습니다.
            Returns:
                각 기사의 본문을 string으로 리턴합니다.
    """
    response = requests.get(_url_, headers={"User-Agent": "Mozilla/5.0"})  # response객체
    soup = BeautifulSoup(response.content, "html.parser", from_encoding='utf-8')  # 한글 깨짐 방지 encoding
    # parsing ,  response객체에서 .content로 html을 추출해서(string) bs4로 parsing합니다.
    content_texts = soup.select('#dic_area')  # bs4객체의 메소드 select사용,
    resoup_ = BeautifulSoup(str(content_texts), "html.parser")  # 다시 parsing
    return resoup_.get_text()  # 사람이 읽을 수 있는 글자만 추출


# 제목 추출 함수
def title(_url_=''):
    """
        content(url)
            ARGS:
                url = info_class[i] , info_class deque에 담긴 각 요소를 인자로 받습니다.
            Returns:
                각 기사의 제목을 string으로 리턴합니다.
    """
    response = requests.get(_url_, headers={"User-Agent": "Mozilla/5.0"})  # response객체
    soup = BeautifulSoup(response.content, "html.parser", from_encoding='utf-8')  # 한글 깨짐 방지 encoding
    # parsing ,  response객체에서 .content로 html을 추출해서(string) bs4로 parsing합니다.
    head_line = soup.select(".media_end_head_headline")  # bs4객체의 메소드 select사용, css class로 검색할 수 있습니다. class = 'media_end_head_headline'
    resoup_ = BeautifulSoup(str(head_line), "html.parser")  # 다시 parsing
    return resoup_.get_text()  # 사람이 읽을 수 있는 글자만 추출


# 기사 입력 날짜 추출
def date(_url_=''):
    """
        title(url)
            ARGS:
                url = info_class[i] , info_class deque에 담긴 각 요소를 인자로 받습니다.
            Returns:
                각 기사의 날짜를 string으로 리턴합니다.
    """
    response = requests.get(_url_, headers={"User-Agent": "Mozilla/5.0"})  # response객체
    soup = BeautifulSoup(response.content, "html.parser", from_encoding='utf-8')  # 한글 깨짐 방지 encoding
    # parsing ,  response객체에서 .text로 html을 추출해서(string) bs4로 parsing합니다.
    head_info = soup.select_one('.media_end_head_info_datestamp_time._ARTICLE_DATE_TIME')  # bs4객체의 메소드 slect사용, css class로 검색할 수 있습니다.
    # class="media_end_head_info_datestamp_time._ARTICLE_DATE_TIME" 입력날짜를 추출합니다.
    resoup_ = BeautifulSoup(str(head_info), "html.parser")  # 다시 parsing
    date_ = resoup_.get_text()  # 사람이 읽을 수 있는 글자만 추출
    return date_


def make_df():  # 주어진 raw_data를 바탕으로 dataframe을 만듭니다.
    """
        make_raw_data()
            ARGS:
                None
            Returns:
                pd.DataFrame object
    """
    def make_raw_data(naver_news=[]):  # 데이터프레임의 column에 들어갈 각 리스트(주소, 제목, 본문, 일자)를 만듭니다.
        """
            make_raw_data()
                ARGS:
                    naver_news -> 네이버뉴스 마킹된 URL로 구성된 리스트
                Returns:
                    None
        """
        queue_ = naver_news
        while queue_:  # 페이지의 모든 기사 제목의 링크를 방문해서 필요한 정보 수지
            url_q = queue_.popleft()
            link_list.append(url_q)  # URL 은 바로 넣어도 됩니다.
            _title = title(url_q)
            _date = date(url_q)
            _content = content(url_q)
            title_list.append(_title)
            content_list.append(_content)
            date_list.append(_date)
        return
    next_ = []
    link_list = deque()
    title_list = deque()
    content_list = deque()
    date_list = deque()
    while True:
        naver_news_list = find_naver_news()  # 네이버뉴스 URL을 담은 큐
        make_raw_data(naver_news_list)  # raw data 제작,각 리스트에 값들을 넣는 함수
        next_.extend(driver.find_elements(By.CLASS_NAME, "btn_next"))
        # 다음 페이지로 넘어가는 버튼을 next_ 리스트에 넣습니다.
        # find_elements의 return이 리스트이기 때문에 extend사용
        driver.implicitly_wait(1)  # 1초 대기
        obj = next_.pop()
        if obj.get_attribute("aria-disabled") == "false":
            obj.click()
        else:
            print('마지막 페이지 입니다.')
            break
    raw_dict = dict()  # 반복문 종 후, 즉 모든 페이지를 넘긴 후 데이터 프레임을 만듭니다.
    raw_dict['titles'] = title_list
    raw_dict['links'] = link_list
    raw_dict['dates'] = date_list
    raw_dict['contents'] = content_list
    return pd.DataFrame(raw_dict)


temp = make_df()
# df = make_df()
# df.to_csv("oasis_navernews.csv")  # csv로 바꿔서 저장합니다.
driver.quit()