from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import requests
from stock_analyzer import Stockalyzer

class Screener:
    def __init__(self, url):
        html = requests.get(url=url, ).text
        self.soup = BeautifulSoup(html, 'html.parser')

    def stripTags(self, full_str):
        col_n = full_str
        while col_n.find('<') != -1:
            start = col_n.find('<')
            end = col_n.find('>')
            col_n = col_n[:start] + col_n[end + 1:]
        newl = col_n.find('\n')
        if newl != -1:
            col_n = col_n[:newl] + col_n[newl+2:]
        return col_n

    def getList(self):
        indx = []
        for col in self.soup.table.tr.contents:
            col_name = str(col)
            col_name = self.stripTags(col_name)
            if col_name:
                indx.append(col_name)
        s_list = []
        for row in self.soup.table.find_all('tr')[1:]:
            s = []
            for i in row.find_all('td'):
                n = self.stripTags(str(i))
                s.append(n)
            if len(s) == 9:
                s = pd.Series(s, index=indx)
                s_list.append(s)
        df = pd.concat(s_list, axis=1).T
        return df.iloc[:,:2]

    def getData(self, list):
        indx = list.columns.values.tolist()
        indx.extend(['Analysis', 'Price', 'Stop', 'Sell'])
        s_list = []
        for index, row in list.iterrows():
            try:
                sto = Stockalyzer(row['Symbol'])
                s = pd.Series([row['Symbol'],
                                  row['Security'],
                                  sto.getAnalysis(),
                                  sto.getPrice(),
                                  sto.getStopPrice(),
                                  sto.getSellPrice()], index=indx)
                s_list.append(s)
            except Exception as ex:
                print(row['Symbol'], 'Error Getting Data:', ex)
        df = pd.concat(s_list, axis=1).T
        return df

    def getBuy(self, data):
        df = data.loc[data['Analysis'] == 'Buy']
        return df