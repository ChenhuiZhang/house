from bs4 import BeautifulSoup
from pandas import Series, DataFrame
from datetime import datetime
import pandas as pd
import requests
import json
import os
import re

base_url = "https://su.lianjia.com/chengjiao"
#first_url = "/c2311049501278/?sug="
first_url = "/c239821887922299/?sug="

def parse_all_page_urls(contents):
    page_urls = []
    soup = BeautifulSoup(contents, 'html.parser')
    page = soup.find('div', {'class': 'contentBottom'}).find('div', {'comp-module': 'page'})
    total = json.loads(page['page-data'])['totalPage']
    current = json.loads(page['page-data'])['curPage']
    for i in range(current, total):
        url = base_url + page['page-url'].replace("{page}", str(i + 1))
        page_urls.append(url)

    return page_urls


def parse_to_df(files):
    region = []
    area = []
    area_num = []
    info = []
    date = []
    total_price = []
    avg_price = []
    init_price = []
    deal_time = []

    for f in files:
        with open(f, 'r') as file:
            soup = BeautifulSoup(file)
            #print(soup.prettify())

            contents = soup.find('ul', {'class': 'listContent'})

            for i in contents.find_all('div', {'class': 'info'}):
                t = i.find('div', {'class': 'title'}).contents[0].string
                print(t.split())
                region.append(t.split()[0])
                #region.append(t.split()[0])
                if len(t.split()) > 2:
                    area.append(t.split()[2])
                else:
                    area.append("15平米")
                house_info = i.find('div', {'class': 'address'}).contents[0].contents[1]
                info.append(t.split()[1] + "|" + house_info)
                deal_date = i.find('div', {'class': 'address'}).contents[1].string
                dt = datetime.strptime(deal_date, '%Y.%m.%d')
                date.append(dt)
                price = i.find('div', {'class': 'address'}).contents[2].span.text
                total_price.append(price)
                #print(i.find('div', {'class': 'flood'}).contents[0].contents[1])
                price = i.find('div', {'class': 'flood'}).contents[2].span.text
                avg_price.append(price)
                if i.find('div', {'class': 'dealHouseInfo'}):
                    print(i.find('div', {'class': 'dealHouseInfo'}).contents[1])
                    print(i.find('div', {'class': 'dealHouseInfo'}).contents[1].contents[0].text)
                if i.find('div', {'class': 'dealCycleeInfo'}):
                    tmp = (i.find('div', {'class': 'dealCycleeInfo'}))
                    if len(tmp.contents[1]) > 1:
                        price = i.find('div', {'class': 'dealCycleeInfo'}).contents[1].contents[0].text
                        init_price.append(price)
                        duration = (i.find('div', {'class': 'dealCycleeInfo'}).contents[1].contents[1].text)
                        deal_time.append(duration)
                    else:
                        print(tmp)
                        init_price.append("0")
                        duration = i.find('div', {'class': 'dealCycleeInfo'}).contents[1].contents[0].text
                        deal_time.append(duration)
                else:
                    init_price.append(0)
                    deal_time.append(0)

                print("###########################")


    print(area)
    for a in area:
        s = [float(s) for s in re.findall(r'-?\d+\.?\d*', a)]
        #area_num.append(int(s[0] / 20) * 20)
        area_num.append(int(s[0]))

    data = {'house': Series(region),
            'area': Series(area_num),
            'info': Series(info),
            'date': Series(date),
            'total_price': Series(total_price),
            'avg_price': Series(avg_price),
            'init_price': Series(init_price),
            'deal_time': Series(deal_time),
            }

    df = DataFrame(data)

    print(df.info())
    print(df)

    df.to_csv("house.csv", encoding='utf_8_sig')

def fetch_info(region="绿地华尔道"):

    print(region)
    r = requests.get(base_url + first_url + region)

    with open(region + '0.html', 'w') as file:
        file.write(r.text)

    for idx, url in enumerate(parse_all_page_urls(r.text)):
        r = requests.get(url)

        f_name = region + str(idx+1) + ".html"
        with open(f_name, 'w') as file:
            file.write(r.text)


#fetch_info("加城花园")

files = [f for f in os.listdir('.') if (os.path.isfile(f) and os.path.splitext(f)[1] == ".html")]
print(files)

parse_to_df(files)
