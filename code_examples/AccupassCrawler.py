from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import json

class AccuPassSite(object):
    '''此類別用以擷取
       http://http://www.accupass.com/
       上的活動資訊。'''
    def __init__(self,browser):
        '''初始化一些即將用來儲存資訊的清單，以及開啟瀏覽器。'''
        self.baseURL = 'http://www.accupass.com/event/register/'
        self.eventURLs = []
        self.eventPeriods = []
        self.eventNames = []
        self.browser = browser
        self.numOfPages = None

    def soupRetriever(self,url,maxRetryTime=20):
        '''擷取soup直到成功或次數超過maxRetryTime。'''
        i=0
        while(i<=maxRetryTime):
            print("第%i次擷取"%(i+1) ,end='  ')
            self.browser.get(url)
            text = self.browser.page_source
            self.soup = BeautifulSoup(text, 'lxml')
            cards = self.soup.select('div .apcss-activity-card')
            if(len(self.soup)!=0 and len(cards)!=0):
                print('...擷取成功')
                return self
            else:
                pass
            i+=1
            if(i==maxRetryTime):
                raise Exception('Tried many times but failed to retrieve what we want!')

    def numOfPagesRetriever(self):
        '''由soup去判定總共有幾個頁面需要擷取，並將此資訊存於self.numOfPages。'''
        if(self.numOfPages==None):
            numOfPagesInfo = self.soup.select(".pagination")[0].select("li:nth-of-type(14)")[0].a["ng-click"][27:-1]
            self.numOfPages = json.loads(numOfPagesInfo)['CurrentIndex']
            print("total number of pages=",self.numOfPages)
        else:
            pass
        return self

    def colsRetriever(self):
        '''從擷取到的soup內，去提取(retrieve)出我們所需欄位(columns)的資訊。
           我們想取得的資訊分別為：活動名稱(eventNames)，活動發生時間(eventPeriods)以及活動網址(eventURLs)。
           這些資訊將以清單的方式被儲存。
        '''
        divs = self.soup.select("div[class='col-xs-12 col-sm-6 col-md-4 ng-scope']")
        for div in divs:
            dic = json.loads(div.div['event-row'])
            self.eventURLs.append(self.baseURL+dic['eventIdNumber'])
            self.eventPeriods.append(dic['fullDateTimeStr'])
            self.eventNames.append(dic['name'])
        return self

    def toFrame(self):
        '''將清單eventNames, eventPeriods和eventURLs組合成為一個DataFrame。'''
        self.df = pd.DataFrame({"eventName": self.eventNames, "eventPeriod": self.eventPeriods, "eventURL": self.eventURLs})
        return self.df

#browser = webdriver.Chrome('/Users/chweng/Desktop/chromedriver')
browser=webdriver.PhantomJS()                        #開啟輕量瀏覽器PhantomJS。

site=AccuPassSite(browser)

j=0
while( site.numOfPages==None or j<site.numOfPages):  #此迴圈將一次抓取一個頁面上的所有活動。註：一個頁面的資訊將會存成一個soup。
    print("\nthis is loop %d."%j)
    url='https://www.accupass.com/search/r/1/0/6/1/1/'+str(j)+'/20120101/20161231'
    site.soupRetriever(url).numOfPagesRetriever().colsRetriever()  # 1.擷取soup 2.若是第一次跑則判斷總共有幾個soup要擷取 3.從soup中擷取欄位資訊
    j+=1

browser.quit()                                       #關閉瀏覽器。
site.toFrame().to_csv("activities_accupass.csv")     #將擷取下來的資訊轉成DataFrame後直接存成csv。