import requests
import re
import time
import bs4
import openpyxl
import xlwt
from lxml import etree
import pymongo
headers ={'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}

result1=[]
links=['https://movie.douban.com/top250?start={}&filter='.format(str(i*25))for i in range(0,10)]
messages=[]
xx=[]
oo=[]
link22=[]
book=xlwt.Workbook(encoding='utf-8',style_compression=0)
sheet=book.add_sheet('a',cell_overwrite_ok=True)
sheet.write(0,0,'title')
sheet.write(0,1,'score')
sheet.write(0,2,'info')
sheet.write(0,3,'link')
            
n=1
def main():
      for link in links:
          r=requests.get(link,headers=headers)
          html=r.content
          '''print(r.status_code)'''
          #print(r.text)
          soup=bs4.BeautifulSoup(r.text,'html.parser')
          '''depth=soup.find('span',class_='next').previous_sibling.previous_sibling.text

          depth=int(depth)'''
          contents=soup.find_all('div',class_='hd')
          selector = etree.HTML(html)
          link2=selector.xpath('//div[@class="hd"]/a/@href')
          for each in link2:
              
              link22.append(each)
          for each in contents:
              xx.append(each.a.span.text)
          authors=soup.find_all('div',class_='bd')
          
          for each in authors:
              try:
                    messages.append(each.p.text.split('\n')[1].strip()+each.p.text.split('\n')[2].strip())
              except:
                    continue
          comments=soup.find_all('span',class_='rating_num')
          for each in comments:
              oo.append(each.text)
      for i in range(0,250):
            result1.append(xx[i]+'评分:'+oo[i]+messages[i]+'\n')
      save(result1)
      save_ex(xx,oo,messages,link22)
      book.save('doubantop.xlsx')
      save_pymongo(xx,oo,messages,link22)
      print('***finish')
def save(result1):
      with open('doubantop.txt','w',encoding='utf-8')as f:
            for each in result1:
                f.write(each)
def save_ex(xx,oo,messages,link22):
      for i in range(0,250):
            
            global n
            sheet.write(n,0,xx[i])
            sheet.write(n,1,oo[i])
            sheet.write(n,2,messages[i])
            sheet.write(n,3,link22[i])
            
    
            n=n+1
      print('fin  ex')

def save_pymongo(xx,oo,messages,link22):
    myclient=pymongo.MongoClient("mongodb://localhost:27017/")
    mydb=myclient['douban']
    mycol=mydb['dddd']
    for i in range(0,10):

        xx1={'title':xx[i],'score':oo[i],'messages':messages[i],'link22':link22[i]}

        mycol.insert_one(xx1)


main()








'''names=re.findall('<span class="other">&nbsp;/&nbsp;(.*?)</span>',r.content.decode('utf-8'),re.S)
    for name,author,content in zip(names,authors,contents):
        list1.append(name+author+content+'\n')
        
    time.sleep(1)'''
