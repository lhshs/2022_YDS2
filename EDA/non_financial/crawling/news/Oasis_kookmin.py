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

# tqdm : for문 진행상황 체크
from tqdm import tqdm, tqdm_notebook
from tqdm.notebook import tqdm

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

# 변수 초기화, Web page 초기화
# title_list = deque()
# link_list = deque()
# date_list = deque()
# content_list = deque()
# press_list = deque()
#
# driver.quit()

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

# 언론사 필터 열기
# find_elements로 리스트로 return후 인덱스로 element에 접근
press_list = driver.find_elements("css selector", "a.txt.txt_option._category_select_trigger")
driver.implicitly_wait(2)
driver.execute_script("arguments[0].click();", press_list[0])  ## JS_Executor로 script 실행

# 일간지 선택
daily_newpaper = driver.find_elements(By.XPATH, '//*[@id="snb"]/div[2]/ul/li[4]/div/div[1]/a[2]')
driver.implicitly_wait(2)
driver.execute_script("arguments[0].click();", daily_newpaper[0])  ## JS_Executor로 script 실행

# 언론사 목록 만들기
media_outlets_str = '경향신문 국민일보 내일신문 동아일보 매일일보 문화일보 서울신문 세계일보 아시아투데이 전국매일신문 조선일보 중앙일보 천지일보 한겨례 한국일보'
temp = media_outlets_str.split()
media_outlets = dict()  # key == 일간지 이름, value == XPATH(str)
for i, v in enumerate(temp):
    media_outlets[v] = f'//*[@id="snb"]/div[2]/ul/li[4]/div/div[2]/div/div[2]/div/div/div/ul/li[{i + 1}]/a'  # f-string

"""
media_outlets['경향신문'] = '//*[@id="snb"]/div[2]/ul/li[4]/div/div[2]/div/div[2]/div/div/div/ul/li[1]/a'
media_outlets['국민일보'] = '//*[@id="snb"]/div[2]/ul/li[4]/div/div[2]/div/div[2]/div/div/div/ul/li[2]/a'
.... li[num] -> num 1~15
media_outlets['한국일보'] = '//*[@id="snb"]/div[2]/ul/li[4]/div/div[2]/div/div[2]/div/div/div/ul/li[15]/a'
"""


def click_press(daily_name='국민일보'):  # daily_name(일간지 명) is str
    """
        click_press('한국일보')
            ARGS:
                daily_name = '한국일보'
            Returns:
                현재 페이지의 URL
    """
    press = driver.find_elements(By.XPATH, media_outlets[daily_name])
    driver.implicitly_wait(2)
    driver.execute_script("arguments[0].click();", press[0])  ## JS_Executor로 script 실행
    return driver.current_url  # 현재 페이지의 URL을 가져옵니다.


def page_count(url=''):  # 페이지 수 세기
    """
        page_count(url)
            ARGS:
                url = click_press(daily_name) -> click_press return URL
            Returns:
                현재 url의 페이지 수
    """
    response = requests.get(url)
    soup_ = BeautifulSoup(response.text, "html.parser")  # parsing
    sc_page_inner_ = soup_.select('.sc_page_inner')  # 페이지 수를 찾기위해서 sc_page_inner class로 markup 찾기,
    # return : bs4.element.Resultset 파이썬의 리스트와 유사합니다.
    soup_2 = BeautifulSoup(str(sc_page_inner_[0]),
                           "html.parser")  # bs4.element.Resultset에서 인덱스로 요소에 접근하고,string으로 변환하고 다시 parsing했습니다.
    a_tags = soup_2.find_all('a')  # a 태그만 찾기. a tag -> href, page 별로 각 하이퍼링크가 존재합니다.
    return len(a_tags)


# 본문 추출 함수(국민일보)
def content(_url_=''):
    """
          content(url)
            ARGS:
                url = contents_links.popleft() -> contents_links에 dequeue구조로 한 페이지의 각 기사의 하이퍼링크가 걸려있습니다.
            Returns:
                각 기사의 본문을 string으로 리턴합니다.
    """
    response = requests.get(_url_, headers={"User-Agent": "Mozilla/5.0"})  # response객체
    soup = BeautifulSoup(response.content.decode('euc-kr', 'replace'), "html.parser")  # 한글 깨짐 방지 decoding
    # parsing ,  response객체에서 .text로 html을 추출해서(string) bs4로 parsing합니다.
    content_texts = soup.select('#articleBody')  # bs4객체의 메소드 select사용, css select에서 id로 찾기 id = articleBody
    resoup_ = BeautifulSoup(str(content_texts), "html.parser")  # 다시 parsing
    return resoup_.get_text()  # 사람이 읽을 수 있는 글자만 추출


# 제목 추출 함수(국민일보)
def title(_url_=''):
    """
        title(url)
            ARGS:
                url = contents_links.popleft() -> contents_links에 dequeue구조로 한 페이지의 각 기사의 하이퍼링크가 걸려있습니다.
            Returns:
                각 기사의 제목을 string으로 리턴합니다.
    """
    response = requests.get(_url_, headers={"User-Agent": "Mozilla/5.0"})  # response객체
    soup = BeautifulSoup(response.content.decode('euc-kr', 'replace'), "html.parser")  # 한글 깨짐 방지 decoding
    # parsing ,  response객체에서 .text로 html을 추출해서(string) bs4로 parsing합니다.
    head_line = soup.select('h3')  # bs4객체의 메소드 slect사용, tag로 검색할 수 있습니다. tag=<h3> 제목 클래스 모두 찾기
    resoup_ = BeautifulSoup(str(head_line), "html.parser")  # 다시 parsing
    return resoup_.get_text()  # 사람이 읽을 수 있는 글자만 추출


# 기사 입력 날짜 추출(국민일보)
def date(_url_=''):
    """
        title(url)
            ARGS:
                url = contents_links.popleft() -> contents_links에 dequeue구조로 한 페이지의 각 기사의 하이퍼링크가 걸려있습니다.
            Returns:
                각 기사의 날짜를 string으로 리턴합니다.
    """
    response = requests.get(_url_, headers={"User-Agent": "Mozilla/5.0"})  # response객체
    soup = BeautifulSoup(response.content.decode('euc-kr', 'replace'), "html.parser")  # 한글 깨짐 방지 decoding
    # parsing ,  response객체에서 .text로 html을 추출해서(string) bs4로 parsing합니다.
    head_line = soup.select_one('.t11')  # bs4객체의 메소드 slect사용, css class로 검색할 수 있습니다. class = t11 입력날짜를 추출합니다.
    resoup_ = BeautifulSoup(str(head_line), "html.parser")  # 다시 parsing
    date_ = resoup_.get_text()  # 사람이 읽을 수 있는 글자만 추출
    return date_


# url 그대로 return 하는 함수
def link_url(_url_=''):
    return _url_


# 제목 & 링크 & 본문 & 발행일 저장 -> Dataframe화
def make_df():
    contents_links = deque()  # 현재 페이지(1페이지)에서 모든 기사 하이퍼링크 찾기
    titles = driver.find_elements('css selector', 'a.news_tit')  # 페이지 각 기사 제목별로 하이퍼링크가 걸려있습니다.
    for i, v in enumerate(titles):
        contents_links.append(v.get_attribute('href'))  # 각 하이퍼링크 순서로 queue에 넣기
    title_list = deque()
    link_list = deque()
    content_list = deque()
    date_list = deque()
    while contents_links:  # 페이지의 모든 기사 제목의 링크를 방문해서 필요한 정보 수지
        url_q = contents_links.popleft()
        _title = title(url_q)
        _link = link_url(url_q)
        _date = date(url_q)
        _content = content(url_q)
        title_list.append(_title)
        link_list.append(_link)
        content_list.append(_content)
        date_list.append(_date)
    raw_dict = dict()
    raw_dict['titles'] = title_list
    raw_dict['links'] = link_list
    raw_dict['dates'] = date_list
    raw_dict['contents'] = content_list
    return pd.DataFrame(raw_dict)


press_url = click_press('국민일보')  # 국민일보 클릭
pages_ = page_count(press_url)  # 국민일보의 페이지 수 Return


total = dict()  # 페이지별로 딕셔너리의 Value로 저장하였습니다.
for _ in range(pages_):
    total[_] = make_df()
    driver.find_element("css selector", 'a.btn_next').click()   # 다음 페이지 클릭

result_df = pd.DataFrame()  # 딕셔너리의 Value로 각 페이지별 데이터프레임을 합쳤습니다.
for _ in range(pages_):
    result_df = result_df.append(total[_])

result_df.to_csv("oasis_kookmin.csv")  # csv로 바꿔서 저장합니다.


