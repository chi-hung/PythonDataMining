#!/usr/local/bin/python3

import requests
import re
import datetime
import random
from time import sleep
import bs4
from bs4 import BeautifulSoup
import pandas as pd
from pandas import Series, DataFrame
import sqlalchemy
from sqlalchemy import create_engine,Table,Column,Integer,String,MetaData,ForeignKey,Date,update
import warnings
import multiprocessing as mp

class ReviewsExtracter:
	def Authors(self,soup,ProdId):
		#擷取評論者 &產品ID
		list_author=[]
		list_prodid=[]
		rAuthors=soup.select('div[data-hook="review"]')

		for author in rAuthors:
			ath=author.div.next_sibling.span.get_text("|",strip=True).split("|")
			if(len(ath)==1):
				list_author.append(ath[0])
			else:
				list_author.append(ath[1])
			list_prodid.append(ProdId)
		return list_author,list_prodid                              

	def Stars(self,soup):
		#擷取星星數
		list_star=[]
		Rstars=soup.select("i[data-hook='review-star-rating']")
		for star in Rstars:
			star=re.sub('[a-zA-Z].+s','',star.text).split(' ')[0][0]
			fStar=int(star)
			list_star.append(fStar)
		return list_star

	def Dates(self,soup):
		#擷取日期
		list_date=[]
		rDates=soup.select("span[data-hook='review-date']")
		for date in rDates:
			date2=(date.text)[3:]
			date3=datetime.datetime.strptime(date2, '%B %d, %Y').strftime('%Y-%m-%d')
			list_date.append(date3)
		return list_date    

	def Title(self,soup):
		#擷取評論主旨
		list_title=[]
		rtitle=soup.select("a[data-hook='review-title']")
		for title in rtitle:
			list_title.append(title.text)
		return list_title

	def Reviews(self,soup):
		#擷取評論內容
		list_review=[]
		reviews=soup.select("span[class='a-size-base review-text']")
		for review in reviews:
			list_review.append(review.get_text(separator="\n\n",strip=True))
		return list_review

	def Verifieds(self,soup):
		#擷取購買驗證
		list_verified=[]
		rVerifieds=soup.select('div[class="a-row a-spacing-mini review-data review-format-strip"]')
		a=0
		for verified in rVerifieds :
			if 'Verified' in verified.text:
				ver=1
				a+=1
			else:
				ver=0
				a+=1
			list_verified.append(ver)
		return list_verified  

	def Comments(self,soup):
		#擷取評論回覆數
		list_comment=[]
		rcomments = soup.select('span[class="review-comment-total aok-hidden"]')
		for comment in rcomments:
			list_comment.append(comment.text)
		return list_comment     

	def Helps(self,soup):
		#擷取覺得有幫助的人數
		list_helps=[]
		tagsHelps=soup.select('span[class="cr-vote-buttons"] > span[class="a-color-secondary"]')
		idx=0
		for helps in tagsHelps:
			if "One" in helps.text:
				NumPeopleFindHelpful=1
			elif (helps.span==None):
				NumPeopleFindHelpful=0    
			else:
				NumPeopleFindHelpful=int(re.sub('[^0-9]', '',(helps.text)))
			idx+=1             
			list_helps.append(NumPeopleFindHelpful)
		return list_helps
	
	def Crawler(self,ProdId,ProdName,totalNumReviews,maxretrytime=60): 
		"""
		此函數輸入ProdId,ProdName,reviews
		輸出為含有Amazon評論等資訊的表單
		"""
		url_base ="https://www.amazon.com/"
		url_01 = "/product-reviews/"
		url_02="/ref=cm_cr_arp_d_paging_btm_1?pageNumber="
		url_03="&reviewerType=all_reviews&pageSize=50"
		#決定要換多少頁
		totalNumPages=int(totalNumReviews/50)+2

		list_prodid=[]
		list_author=[]
		list_star=[]
		list_date=[]
		list_title=[]
		list_review=[]
		list_verified=[]
		list_comments=[]
		list_helps=[]

		for currentPageNum in range(1,totalNumPages+1):
			print("ProdId= %s. Total number of pages= %s. Current page= %s."%(ProdId,totalNumPages,currentPageNum) )
			passed=False
			cnt=0
			while(passed==False):
				cnt+=1
				if(cnt>maxretrytime):
					raise Exception("Error! Tried too many times but we are still blocked by Amazon.")
					print("ProdId="+ProdId+","+"CurrentPage="+currentPageNum)
				try:
					# 建立連線
					with requests.Session() as session:
						#session.headers = {'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0"}
						uri=url_base+ProdName+url_01+ProdId+url_02+str(currentPageNum)+url_03
						r=session.get(uri)

						if(r.status_code!=200):
							print("Connection failed(status/=200). Reconnecting...")
							sleep(0.3)
						else:
							# 回應200則獲取湯
							soup = BeautifulSoup(r.content,"lxml")
							#print(soup.prettify())
							# 若發現湯是假的，就小睡數秒，之後再重複獲取一次湯。若重複獲取湯的次數超過maxretrytime，程式將終止
							if("Robot Check" in soup.text):
								print("we are identified as a robot! Reconnecting...")
								sleep(0.2+0.1*random.randint(0,1)) # 睡 0.2 或 0.3 秒
								if(cnt>25):
									sleep(0.5)                 	 # 要是一直不行(重試超過25次)，不如就再多睡0.5秒吧
							else:
								print("We've obtained the correct soup!")
								passed=True
								lst_author,lst_prodid=self.Authors(soup,ProdId)  #評論者與ProdId 分別放到2個列表
								lst_star=self.Stars(soup)                        #星星數
								lst_date=self.Dates(soup)                        #日期
								lst_title=self.Title(soup)                       #評論主旨
								lst_review=self.Reviews(soup)                    #評論內容
								lst_verified=self.Verifieds(soup)                #購買驗證
								lst_comments=self.Comments(soup)                 #評論回覆數
								lst_helps=self.Helps(soup)                       #覺得有幫助的人數
						
								print("URL=",uri)
								lengths=[len(lst_prodid),len(lst_author),len(lst_star),len(lst_date),len(lst_title),len(lst_review),len(lst_verified),len(lst_comments),len(lst_helps)]
								if(len(set(lengths))!=1):
									print(lengths)
									warnings.warn('Beware. Lists obtained have no equal length.')
									print("length of lst_prodid=",len(lst_prodid))       
									print("length of lst_author=",len(lst_author))
									print("length of lst_star=",len(lst_star))
									print("length of lst_date=",len(lst_date))
									print("length of lst_title=",len(lst_title))
									print("length of lst_review=",len(lst_review))
									print("length of lst_verified=",len(lst_verified))
									print("length of lst_comments=",len(lst_comments))
									print("length of lst_helps=",len(lst_helps))           
				except:
					print("Error encounted! ProdId= "+ProdId+". "+"Current Page= "+str(currentPageNum))
					print("The error is probably caused by connection time out? Reconnecting...")
					sleep(0.3)

			list_prodid+=lst_prodid
			list_author+=lst_author
			list_star+=lst_star
			list_date+=lst_date
			list_title+=lst_title
			list_review+=lst_review
			list_verified+=lst_verified
			list_comments+=lst_comments
			list_helps+=lst_helps
		
		df=pd.DataFrame.from_items([("pindex",list_prodid),("author",list_author),("star",list_star),\
									 ("date",list_date),("title",list_title),("review",list_review), \
									 ("verified",list_verified),("comment",list_comments),("help",list_helps)])\
			 .drop_duplicates("review").reset_index(drop=True)
		return df
	
	def prodInfoFetcherForCrawler(self,thisCrawlerID,prodType):
		"""
		the crawler needs to know who are the items that their reviews are not fetched yet and the webpage of those items.
		This method fetches those necessary informations that the crawler needs to know.
		"""
		prodTypes=["central","canister","handheld","robotic","stick","upright","wetdry"]

		engine=create_engine("mysql+pymysql://semantic:GbwSq1RzFb@104.199.201.206:13606/semantic?charset=utf8mb4",echo=False, encoding='utf-8')
		conn = engine.connect()

		sql_command = "SELECT pindex,pname,totalRev,cID,cStatus FROM semantic.amzProd where type='"+ prodType +"' \
		and cStatus!=1 and cID="+str(thisCrawlerID)+" ORDER BY totalRev desc"
		resultSet = pd.read_sql_query(sql=sql_command, con=conn, coerce_float=False)

		conn.close()

		return resultSet
	
	def prodRevstoSQL(self,ProdId,resultTable):
		"""
		this method will upload the fetched customer reviews of a single product to the SQL server
		"""
		prodTypes=["central","canister","handheld","robotic","stick","upright","wetdry"]

		# prepare the connection and connect to the DB
		engine=create_engine("mysql+pymysql://semantic:GbwSq1RzFb@104.199.201.206:13606/semantic?charset=utf8mb4",convert_unicode=True,echo=False)
		conn = engine.connect()
	
		resultTable.to_sql(name='amzRev', con=conn, if_exists = 'append', index=False)

		sql_command = "UPDATE semantic.amzProd SET cStatus=1 where pindex='"+ ProdId +"'"
		result = conn.execute(sql_command)
		# close the connection
		conn.close()
	
	def run(self,begin,end,incr,resultSet,nRows,nCols):
		"""
		this function will fetch customer reviews of a single product
		"""
		for j in range(begin,end,incr):
			print("this is item %i of %i items"%(j+1,nRows))
			ProdId,ProdName,NumReviews=resultSet.loc[j,["pindex","pname","totalRev"]]
			print(j+1,ProdId,ProdName,NumReviews)
			resultTable=self.Crawler(ProdId,ProdName,NumReviews)
			print("the shape of the obtained table is %s X %s \n"%(resultTable.shape[0],resultTable.shape[1]))
			self.prodRevstoSQL(ProdId,resultTable) 

	def multiThreadedRun(self,resultSet,thisCrawlerID,nThreads):
		if(resultSet.shape[0] >= nThreads):
			nRows,nCols=resultSet.shape[0],resultSet.shape[1]
			print("number of products to be fetched= ",nRows)
			# Let's use 2 threads to finish our task
			for j in range(nThreads):
				print("index of iterations for thread%i= "%j,*range(j,nRows,nThreads))
			processes = [mp.Process(target=self.run, args=(j,nRows,nThreads,resultSet,nRows,nCols,) ) for j in range(nThreads)]
			# start and run the processes
			for p in processes:
				p.start()
			for p in processes:
				p.join()
		else:
			print("this code stopped because number of rows= ",resultSet.shape[0])

prodTypes=["central","canister","handheld","robotic","stick","upright","wetdry"]

###########################################################################################
# INPUT PARAMETERS
prodType=prodTypes[-2] # 指定要爬的吸塵器種類
thisCrawlerID=6        # 指定此爬蟲程式ID
nThreads=1             # 選擇使用多少執行緒來爬蟲
###########################################################################################

extractor=ReviewsExtracter()
resultSet=extractor.prodInfoFetcherForCrawler(thisCrawlerID,prodType)
extractor.multiThreadedRun(resultSet,thisCrawlerID,nThreads)
