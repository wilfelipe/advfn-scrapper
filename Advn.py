from unidecode import unidecode
import pandas as pd
from urllib.parse import urlparse, parse_qs
import requests
from bs4 import BeautifulSoup  

class Advfn:
    
    __dc__ = {'domain': 'https://br.advfn.com/bolsa-de-valores/bovespa/',
            'home': '/cotacao',
            'getYields': '/dividendos/historico-de-proventos',
            'getPrices': '/historico/mais-dados-historicos'}
    
    def __init__(self, codigo):
        self.__link__ = self.__dc__['domain'] + codigo
        
        url = self.__link__ + self.__dc__['home']
        soup = self.__getSoup__(url)
        df = self.__tableSoupToDf__(soup.find('div', {'class': 'TableElement'}))
        self.__dfToAttrs__(df)
        
    #Convert Pandas DataFrames to a object atributes
    def __dfToAttrs__(self, df):
        for column in df.columns:
            name = unidecode(column.strip().replace(' ', '_')).lower()
            value = df[column].iloc[0]
            setattr(self, name, value)
            
    def __getSoup__(self, url):
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}
        response = requests.get(url, headers=headers)
        return BeautifulSoup(response.text, 'html.parser')
    
    def __tableSoupToDf__(self, soup, dic = ''):
        table = soup.find('table', dic).findAll('tr')
        
        header = [[th.text for th in tr.find_all('th')] for tr in table if [th.text for th in tr.find_all('th')] != []]
        data = [[td.text for td in tr.find_all('td')] for tr in table if [td.text for td in tr.find_all('td')] != []]
        
        if len(data[0]) == len(header[0]):
            return pd.DataFrame(data, columns=header[0])
        else:
            return pd.DataFrame()
        
        
    def getYields(self):
        url = self.__link__ + self.__dc__['getYields']

        soup = self.__getSoup__(url)
        df = self.__tableSoupToDf__(soup, {'class': 'dividends'})        
        
        return df    
    
    #Date format dd/mm/yyyy
    def getPrices(self, date_start, date_end):
        url = self.__link__ + self.__dc__['getPrices'] + '?&Date1=' + date_start + '&Date2=' + date_end

        soup = self.__getSoup__(url)
        
        #Getting number of pages for the iteration.
        t = soup.find('a', {'class': 'date-control'})['href']
        latest_page = int(parse_qs(urlparse(t).query)['current'][0])
        
        df = self.__tableSoupToDf__(soup, {'class': 'histo-results'})
        li = [df]
        for page in range(1, latest_page + 1):
            url = self.__link__ + self.__dc__['getPrices'] + '?&Date1=' + date_start + '&Date2=' + date_end + '&current=' + str(page)
            soup = self.__getSoup__(url)
            
            df = self.__tableSoupToDf__(soup, {'class': 'histo-results'}) 
            
            li.append(df)
        
        df = pd.concat(li, axis=0, ignore_index=True)
        
        return df
        
        
        