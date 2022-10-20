# MLT
특정 비상장주식의 주가 하락세 전환 예측 팩터(추세 전환 트리거) 도출
<img width="751" alt="image" src="https://user-images.githubusercontent.com/104045973/196931775-c1cb2c09-282d-433b-b985-deb5e8581281.png">

# 중간 발표
## 역할분배
<img width="1097" alt="image" src="https://user-images.githubusercontent.com/104045973/196933449-cafcdab0-716e-4372-b617-0636fc599e6a.png">

## 기존 프로젝트의 문제점
<img width="1400" alt="image" src="https://user-images.githubusercontent.com/104045973/196933598-5c5175c0-02a3-4a68-a418-461a4f60b656.png">

## 프로젝트 방향 전환
<img width="1452" alt="image" src="https://user-images.githubusercontent.com/104045973/196933683-ba5875d9-4025-4cc7-9350-e45601775dab.png">

### 1. 데이터 부족 문제 해결
#### 종목 단일화
<img width="1901" alt="image" src="https://user-images.githubusercontent.com/104045973/196933897-9f6bc5d2-4abe-4d97-99a6-d2e4ddada8cf.png">

혁신의 숲(https://www.innoforest.co.kr/) 사이트에서 ‘오아시스마켓’의 주식 관련 기업 데이터를 feature로 추가

KOSIS(https://kosis.kr/index/index.do)를 통해 경제종합지수, 경제심리지수, 소비지수, 물가지수, 심리지수 등의 월별 데이터를 가져와서 feature로 추가

KRX 정보데이터시스템(https://data.krx.co.kr/contents/MDC/MAIN/main/index.cmd) 에서 코스피 관련 데이터를 feature로 추가

Opinet(https://www.opinet.co.kr/user/main/mainView.do)에서 국내 유가 관련 데이터를 feature로 추가

### 2. Y값 정의 & Feature selection

**<1차 Feature selection>**

<img width="714" alt="image" src="https://user-images.githubusercontent.com/104045973/196935207-35fc1bf2-62b9-43b6-ba18-28829a8322f8.png">

<img width="558" alt="image" src="https://user-images.githubusercontent.com/104045973/196935234-24308200-c8ca-40ec-86a1-5473d3e66959.png">


y값 = 1일 단위 주가하락세 : (코스피 일일 등락률 - 주가 일일 등락률)이 양의 값(+)인 날짜를 주가의 하락분(1)으로 정의하고, 하루 단위의 주가 하락세를 y값으로 지정하였다.

추후 모델 개선과 논의를 통해 주가 하락세라고 볼 수 있는 기간과 하락 팩터에 대해 정의를 내릴 예정이다.

XGBoost를 이용해서 5일 간격으로 시계열 데이터를 예측하였고, 평가지표로는 NMAE를 사용하였다.

<img width="662" alt="image" src="https://user-images.githubusercontent.com/104045973/196935397-e041ee52-e0d9-470b-be8f-8d3027237b03.png">

Feature Importance를 계산하여 예측모델에 중요하게 작용한 feature들을 찾아내었고, 극미한 영향을 미친 feature 들을 제거하였다. 이렇게 feature 수를 108개에서 45개로 줄일 수 있었다.

추가적으로 주가를 통해 5일, 20일, 60일 단위의 이동평균선과 추세선, 계절성 등에 대한 feature를 추가했다.

**<2차 Feature Selection>**

<img width="758" alt="image" src="https://user-images.githubusercontent.com/104045973/196938180-4304a8fd-3e99-4cfa-b973-6c068c1e719c.png">


남은 feature와 추가한 이동평균선, 추세선, 계절성에 대한 Feature만 놓고 다시 XGBoost를 돌린 상황이다. MAE값은 개선 되었지만, NMAE 값이 산출되지 않는다.

월별 데이터들을 정규분포 난수 생성으로 일별 데이터를 추가하여 Feature Engineering을 진행할 예정이다. NLP 커뮤니티 일간 긍,부정 글 수 feature도 추가할 예정이다.

### 3. 크롤링

<img width="1435" alt="image" src="https://user-images.githubusercontent.com/104045973/196936062-d61ea0d2-b7c7-4150-a72b-fe2a8b2a3b09.png">

1. 비상장주식 38커뮤니티 크롤링

python의 request 모듈에서 요청을 받아서 response객체를 얻고, 이를 bs4로 parsing하여 처리하였습니다.

반복문에서 반복 인자로 URL번호를 변화시켜 title, url, date, content 각각 리스트에 data를 넣고 데이터프레임으로 만들었습니다.

**결과**

<img width="874" alt="image" src="https://user-images.githubusercontent.com/104045973/196936151-dac7d140-6080-4a91-9bc6-8c7bd8d3e053.png">

2. 네이버뉴스 관련 기사 크롤링

위의 방식과 다르게 URL 번호를 반복인자로 사용하지 않고, selenium chrome driver을 활용해 직접 클릭을 하게 구현했습니다. 

<img width="1292" alt="image" src="https://user-images.githubusercontent.com/104045973/196936454-db2d4de7-fdbd-4352-96d6-255869af61b6.png">
>> 회색 '네이버뉴스' 마킹된 기사만 추출했습니다.

** 동작 영상**
https://www.youtube.com/watch?v=fb88IHHbj30

**결과**
<img width="1470" alt="image" src="https://user-images.githubusercontent.com/104045973/196936579-ffe00c55-334d-4835-bfb9-fea2a16fca99.png">

### 4. NLP

1. news data LABELING

<img width="951" alt="image" src="https://user-images.githubusercontent.com/104045973/196936889-76df53d4-1e88-4801-ac65-9969e43c7d00.png">

2. news data POS Tagging

Noun, Adverb, Adjective, Verb 기준으로 추출

<img width="1151" alt="image" src="https://user-images.githubusercontent.com/104045973/196937484-a4cde1af-b5e6-4289-8056-30b7b64d3608.png">

3. news data Vectorize

<img width="1366" alt="image" src="https://user-images.githubusercontent.com/104045973/196937610-f2fa44fe-56ae-4574-9ee9-52753c400955.png">





