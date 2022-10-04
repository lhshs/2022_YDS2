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


# 제목 & 링크 & 본문 & 발행일 저장 -> Dataframe화
def make_df():
    queue_ = find_naver_news()
    link_list = find_naver_news()  # 네이버뉴스 URL을 담은 큐
    title_list = deque()
    content_list = deque()
    date_list = deque()
    while queue_:  # 페이지의 모든 기사 제목의 링크를 방문해서 필요한 정보 수지
        url_q = queue_.popleft()
        _title = title(url_q)
        _date = date(url_q)
        _content = content(url_q)
        title_list.append(_title)
        content_list.append(_content)
        date_list.append(_date)
    raw_dict = dict()
    raw_dict['titles'] = title_list
    raw_dict['links'] = link_list
    raw_dict['dates'] = date_list
    raw_dict['contents'] = content_list
    return pd.DataFrame(raw_dict)


df = make_df()
df.to_csv("oasis_naver_page1.csv")  # csv로 바꿔서 저장합니다.
driver.quit()

# 한 페이지에서 해야할 일
# 각 페이지에서 네이버 뉴스 큐에 넣기
# URL
# 제목
# 일자
# 본문
# 다음 페이지로


# 다음 페이지 클릭
# # find_elements로 리스트로 return후 인덱스로 element에 접근
# driver.implicitly_wait(1)  # 2초 대기
# next_ = driver.find_elements(By.XPATH, "//*[@id=\"main_pack/\"]/div[2]/div/a[2]")  # 다음 페이지로 넘어가는 버튼 클릭
# driver.implicitly_wait(1)  # 2초 대기
# next_.click()
# # driver.execute_script("arguments[0].click();", next_)  ## JS_Executor로 script 실행
