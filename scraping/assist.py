import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta

# 슬랙 메세지
def post_message(token, channel, text):
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+token},
        data={"channel": channel,"text": text})
    print(response)


# 미국 금리지표

def interest_rate():
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

    URL = 'https://fred.stlouisfed.org/series/T10Y2Y'
    res = requests.get(URL, headers = headers )

    res.raise_for_status() # 접속상태 확인
    soup = BeautifulSoup(res.text, "html.parser")  # lxml

    # td class

    my_data = []

    data = soup.find_all("div", attrs={'id' : 'mobile-meta-col'})
    my_data = [x for i in data for x in i.get_text().split()[0:2] ]

    return(my_data)

# print(interest_rate())

# 미국 주식정보

def us_items():

    ticker_list = ['AAPL', 'MSFT', 'BABA']
    data_set = []
    for ticker in ticker_list:
        URL = 'https://finance.yahoo.com/quote/' + ticker + "?p=" + ticker

        res = requests.get(URL)
        res.raise_for_status()  # 접속상태 확인

        soup = BeautifulSoup(res.text, "html.parser")

        data_1 = soup.find("div", attrs={"class": 'D(ib) Mend(20px)'}).find_all("span")
        data_2 = soup.find("div", attrs={"id": 'quote-summary'}).find_all("td")

        data_1_clean = [data.string for data in data_1[:2]]
        # (앞으로) 정규표현식 쓸 때 한번 거르고 - 디테일하게 거르자

        data_set.append([ticker] + data_1_clean)
    return(data_set)


# 한국 주식정보
def korea_items():

    URL = 'https://finance.naver.com/sise/sise_market_sum.nhn?sosok=0&page=1'

    res = requests.get(URL)
    res.raise_for_status() # 접속상태 확인
    soup = BeautifulSoup(res.text, "html.parser")  # lxml

    # tbody - tr
    data_rows = soup.find("table", attrs={"class" : "type_2"}).find("tbody").find_all("tr")  # list

    data = []
    for row in data_rows :
        columns = row.find_all("td")

        if len(columns) <= 1 : continue # 의미없는 데이터 skip

        # data = [column.string for column in columns] # list c
        data.append([column.get_text().strip() for column in columns])

    return(data[0][1:5])

# 한경컨센서스

def hankyung():

    # header
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    # nowDate
    nowDate = datetime.now().strftime('%Y-%m-%d')
    startDate = (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d')

    URL = f'http://consensus.hankyung.com/apps.analysis/analysis.list?sdate=' \
          f'{str(startDate)}&edate={str(nowDate)}&now_page=1&search_value=REPORT_WRITER&report_type=&pagenum=20&search_text=%B1%E8%B0%E6%B9%CE&business_code='

    res = requests.get(URL, headers=headers)
    res.encoding = 'EUC-KR'  ## 신기하다

    res.raise_for_status()  # 접속상태 확인
    soup = BeautifulSoup(res.text, "html.parser")  # lxml

    # td class

    data_1 = soup.find("table").find_all("a", attrs={'href': 'javascript:void(0);'})
    data_2 = soup.find("table").find_all("td", attrs={'class': 'first txt_number'})
    data_3 = soup.find("table").find_all("div", attrs={'class': 'dv_input'})
    # 속성값

    data_1 = [i.string for i in data_1]  # 리스트를 만들어야
    data_2 = [i.string for i in data_2]
    data_3 = [i.a['href'] for i in data_3]

    data = []
    for y, x, z in zip(data_1, data_2, data_3):

        if re.search("삼성|반도체", str(y)) :
            data.append([x, y, 'http://consensus.hankyung.com' + z])

    # # http://consensus.hankyung.com/
    return(data)

# print(*hankyung(), sep='\n') # 와우


# 개선

text0 = f"======================== 지표 및 주가 ========================"
text1 = f"[미국 장단기 금리 차] {interest_rate()}"
text2 = f"[미국주식] {[i for i in us_items()]}"
text3 = f"[한국주식] {korea_items()}"
text4 = f"=========================== 보고서 ==========================="





# # 마무리

myToken = "xoxb-2331042902405-2334084254274-gnWUOCveMjIepNkzgsK9gcv2"

post_message(myToken, "#real-project", text0)
post_message(myToken, "#real-project", text1)
post_message(myToken, "#real-project", text2)
post_message(myToken, "#real-project", text3)
post_message(myToken, "#real-project", text4)
for i in hankyung() :
    post_message(myToken, "#real-project", f"{i}")

