#!/usr/local/bin/python3

from bs4 import BeautifulSoup 	# For HTML parsing
import requests
import re 						# Regular expressions
from time import sleep 			# To prevent overwhelming the server between connections
import pandas as pd 			# For converting results to a dataframe

from sqlalchemy import create_engine,Table,Column,Integer,String,MetaData,ForeignKey,Date
import pymysql 					# We'll need sqlalchemy and pymysql to connect the SQL server
import datetime

import multiprocessing as mp

class ProdInfo:

	vcleaners={"central":11333709011,"canister":510108,"handheld":510114,"robotic":3743561,"stick":510112,"upright":510110,"wetdry":553022}

	def getVacuumTypeUrl(self,vacuumType,pageNum=1):
		'''
		Given one of the following vacuum type: (central,canister,handheld,robotic,stick,upright,wetdry)
		an URL which is of the vacuum cleaners of the chosen vacuum type will be returned.
		'''
		url_type_base="https://www.amazon.com/home-garden-kitchen-furniture-bedding/b/ref=sr_pg_"+str(pageNum)+"?ie=UTF8&node="
		url=url_type_base+str(self.vcleaners[vacuumType])+"&page="+str(pageNum)
		print (url)
		return url

	def getFinalPageNum(self,url,maxretrytime=50):
		'''
		This method aims to obtain the total number of pages to be explored (for a specific vacuum type)
		'''
		passed=False
		cnt=0
	
		while(passed==False):
			cnt+=1
			print("%s times of iteration (getFinalPageNum)"%cnt)
			if(cnt>maxretrytime):
				raise Exception("Error from getFinalPageNum! Tried too many times but we are still blocked by Amazon.")
			# We have a try-catch block here due to 'Connection time out' will raise an Exception
			try:
				with requests.Session() as session:
					session.headers = {'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0"}            
					r=session.get(url)
					if (r.status_code==200):
						soup=BeautifulSoup(r.content,"lxml")
						if("Robot Check" in soup.text):
							print("we are blocked!")
						else:
							tagsFinalPageNum=soup.select("span[class='pagnDisabled']")
							finalPageNum=str(tagsFinalPageNum[0].text)
							passed=True
					else:
						print("Connection failed. Reconnecting...")
			except:
				print("Error from getFinalPageNum(url)! Probably due to connection time out")
		return finalPageNum 

	def InferFinalPageNum(self,vacuumType,pageNum=1,times=10):
		'''
		We found that the total number of pages cannot be obtained with certainty. Hence, we
		infer the value of it, simply by getting its value 10 times and choosing the smallest one.
		'''
		url=self.getVacuumTypeUrl(vacuumType,pageNum)
	
		list_finalpageNum=[]
	
		for j in range(times):
			finalpageNum=self.getFinalPageNum(url)
			list_finalpageNum.append(finalpageNum)
		FinalpageNum=min(list_finalpageNum)
		print("the infered total number of pages=",FinalpageNum)
		return FinalpageNum
	
	def urlsGenerator(self,vacuumType,FinalPageNum):
		"""
		All the URLs of the selected vacuum type will be returned.
		"""
		URLs=[]
		pageIdx=1
		while(pageIdx<=int(FinalPageNum)):
			url_Type="https://www.amazon.com/home-garden-kitchen-furniture-bedding/b/ref=sr_pg_"+str(pageIdx)+"?ie=UTF8&node="
			url=url_Type+str(self.vcleaners[vacuumType])+"&page="+str(pageIdx)
			URLs.append(url)
			pageIdx+=1
		return URLs

	def soupGenerator(self,URLs,maxretrytime=50):    
		"""
		Soups of all the URLs of the selected vacuum type will be returned.
		"""
		soups=[]
		urlindex=0
		for URL in URLs:
			urlindex+=1
			print("urlindex=",urlindex)
			passed=False
			cnt=0    
			while(passed==False):
				cnt+=1
				print("iteration=",cnt)
				if(cnt>maxretrytime):
					raise Exception("Error from soupGenerator(url,maxretrytime=%i)! Tried too many times but we are still blocked by Amazon."%maxretrytime)
				# We have a try-catch block here due to 'Connection time out' will raise an Exception
				try:
					with requests.Session() as session:
			
						session.headers = {'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0"}            
						r=session.get(URL)            
				
						if (r.status_code==200):                
							soup=BeautifulSoup(r.content,"lxml")
							if("Robot Check" in soup.text):
								print("we are blocked!")
							# we'll save the soup only when the status=200 and the page is not anti-robot
							else:
								print("we are not blocked!")
								soups.append(soup)
								passed=True
						else:
							print("Connection failed. Reconnecting...")
				except:
					print("Error from soupGenerator(URLs,maxretrytime=%i! Probably due to connection time out"%maxretrytime)
			
		return soups
	
	def items_info_extractor(self,soups):

		item_links=[]
		item_num_of_reviews=[]
		item_prices=[]
		item_names=[]
		item_ids=[]
		item_brands=[]
		item_avestars=[]
		for soup in soups:
			items=soup.select('li[id^="result_"]')

			for item in items:

				link_item=item.select("a[href$='customerReviews']")

				# ignore those items which contains 0 customer reviews. Those items are irrelevent to us.
				if (link_item !=[]):  

					price_tag=link_item[0].parent.previous_sibling.previous_sibling
					price_main_tag=price_tag.select(".sx-price-whole")
					price_fraction_tag=price_tag.select(".sx-price-fractional")

					link=link_item[0]["href"]

					# Ignore items which don't have normal price tags.
					# Those are items which are not sold by Amazon directly.
					# Also, remove those items which are ads (3 ads are shown in each page).
					if((price_main_tag !=[]) & (price_fraction_tag !=[]) & (link.endswith("spons#customerReviews") == False)):

						# extract the item's name and ID from the obtained link
						item_name=link.split("/")[3]
						item_id=link.split("/")[5]
						# replace the obtained link by the link that will lead to the customer reviews
						base_url="https://www.amazon.com/"
						link=base_url+item_name+"/product-reviews/"+item_id+"/ref=cm_cr_getr_d_paging_btm_" \
									 +str(1)+"?ie=UTF8&pageNumber="+str(1)+"&reviewerType=all_reviews&pageSize=1000"

						# obtain the price of the selected single item
						price_main=re.sub(",","",price_main_tag[0].text)
						price_fraction=price_fraction_tag[0].text
						item_price=int(price_main)+0.01*int(price_fraction)

						# obtain the brand of the selected single item
						item_brand=price_tag.parent.select(".a-size-small")[1].text
						if(item_brand=="by "):
							item_brand=price_tag.parent.select(".a-size-small")[2].text
						# obtain the number of reviews of the selected single item
						item_num_of_review=int(re.sub(",","",link_item[0].text))
					
						# obtain the averaged number of stars
						starSelect=item.select_one("span[class='a-declarative']")
						#starSelect=item.select_one("div[class='a-column a-span5 a-span-last']")


						if(starSelect is None):  # there are no reviews yet (hence, we see no stars at all)
							item_avestar=0
						else:
							item_avestar=starSelect.span.string.split(" ")[0]   # there are some reviews. So, we are able to extract the averaged number of stars
							#item_avestar=starSelect.div.span.a.i.string.split(" ")[0]   # there are some reviews. So, we are able to extract the averaged number of stars
					
						# store the obtained variables into lists
						item_links.append(link)
						item_num_of_reviews.append(item_num_of_review)
						item_prices.append(item_price)
						item_names.append(item_name)
						item_ids.append(item_id)
						item_brands.append(item_brand)
						item_avestars.append(item_avestar)
		return item_brands,item_ids,item_names,item_prices,item_num_of_reviews,item_links,item_avestars

def run(prodType):
	print("The chosen vacuum type is %s.\n"%prodType)
	# retrieve the data we want
	prodObj=ProdInfo()
	FinalPageNum=prodObj.InferFinalPageNum(prodType)
	URLs=prodObj.urlsGenerator(prodType,FinalPageNum)
	soups=prodObj.soupGenerator(URLs)
	item_brands,item_ids,item_names,item_prices,item_num_of_reviews,item_links,item_avestars=prodObj.items_info_extractor(soups)
	# store the retrieved data
	date=datetime.datetime.now().strftime("%Y-%m-%d")
	df=pd.DataFrame.from_items([("pindex",item_ids),("type",prodType),("pname",item_names),("brand",item_brands),("price",item_prices),("rurl",item_links),("totalRev",item_num_of_reviews),("avgStars",item_avestars)])
	df.to_csv("ProdInfo_%s_%s.csv"%(prodType,date), encoding="utf-8")
	## engine=create_engine("mysql+pymysql://semantic:GbwSq1RzFa@104.199.201.206:13606/Tests?charset=utf8",echo=False, encoding='utf-8')
	## conn = engine.connect()
	## df.to_sql(name='amzProd', con=conn, if_exists = 'append', index=False)
	## conn.close()

prodTypes=["central","canister","handheld","robotic","stick","upright","wetdry"]

#run(prodTypes[-1]) # recalculate for the type wetdry

#for prodType in prodTypes:
#	run(prodType)

# Let's use 7 threads to retrieve data of the 7 types of vacuum cleaners
processes = [mp.Process(target=run, args=(prodType,) ) for prodType in prodTypes]
# start and run the processes
for p in processes:
    p.start()
for p in processes:
    p.join()
