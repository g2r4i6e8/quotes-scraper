# -*- coding: utf-8 -*-
"""
Created on Mon Aug  5 13:24:38 2019
@author: Kolomatskiy
"""

from bs4 import BeautifulSoup
from urllib.request import urlopen
import re
import pandas as pd
import os


def processing(result):
    def author(result_set):
        for element in result_set:
            if "Автор цитаты" in str(element) or "Цитируемый персонаж" in str(element):
                return (element.string)

    def stroke(result_set):
        for each in result_set:
            a = str(each.p)
            for link in each.find_all('a'):
                a = a.replace(str(link), link.string)

            if a != 'None': return (re.sub(r"\<(.|.*)\>", '', a).replace('\xa0', ' '))

    quotes = []
    for q in result.find_all('div', 'node__content'):
        quotes.append([stroke(q.find_all('div', 'field-item even last')), author(q.find_all('div', 'field-item even'))])

    return (pd.DataFrame(quotes, columns=['quote', 'author']).drop_duplicates())


def save_to_file(dataframe, name):
    output_path = os.path.join(os.path.dirname(os.getcwd()), 'output', name)
    if not os.path.exists(output_path):
        os.makedirs(output_path)
        print('Directory ', name, ' created')

    for index, row in dataframe.iterrows():
        global count
        quotation = row['quote'] + "\n\n" + row['author']
        path = os.path.join(output_path, str(count) + ".txt")
        with open(path, "w", encoding="ansi") as text_file:
            text_file.write(quotation)

        count += 1

if __name__ == '__main__':
    #open all quotes' topics
    html_doc = urlopen('https://citaty.info/tema').read()
    soup = BeautifulSoup(html_doc, features="lxml")

    #collect urls of all topics' pages
    urls = []
    for topic in soup.find_all('div', 'term-content-wrapper'):
        for link in topic.find_all('a'):
            url = link.get('href')
            urls.append(url)

    #filter unique urls
    urls = list(set(urls))

    #process each topic and save each quote in a separate file
    for url in urls:
        count = 1
        for page in range(0, 50):
            try:
                topic = urlopen(url + '?sort_by=rating&page=' + str(page)).read()
                result = BeautifulSoup(topic, features="lxml")
                quotes = processing(result)
                save_to_file(quotes, url.split('/')[-1])
            except Exception as e:
                pass