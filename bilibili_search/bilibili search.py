from selenium import webdriver,common
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import datetime
import requests
from lxml import etree
import xlwt

book=xlwt.Workbook(encoding='utf-8',style_compression=0)
sheet=book.add_sheet('a',cell_overwrite_ok=True)
n=1
'''option=webdriver.ChromeOptions()
option.add_argument('headless') # 设置option
driver = webdriver.Chrome(options=option)  # 调用带参数的谷歌浏览器????'''
#主页 可能出现 多一个 标题 会错位 一行
def main():
    url='https://www.bilibili.com/'
    driver = webdriver.Chrome()
    
    driver.get(url)
    
    driverwait = WebDriverWait(driver, 20)
    sheet.write(0,0,'title')
    sheet.write(0,1,'date')
    sheet.write(0,2,'link')
    sheet.write(0,3,'link_space')
    sheet.write(0,4,'up')
    content=input('输入内容')
    num=input('输入页数')
    
    search=driverwait.until(EC.element_to_be_clickable((By.XPATH,'//*[@id="nav_searchform"]/input')))
    submit=driverwait.until(EC.element_to_be_clickable((By.XPATH,'//*[@id="nav_searchform"]/div/button')))
    search.send_keys(content)

    submit.click()
    all_h=driver.window_handles
    driver.switch_to.window(all_h[1])
    page_num=driverwait.until(EC.element_to_be_clickable((By.XPATH,'//*[@id="all-list"]/div[1]/div[3]/div/ul/li[8]/button')))
    print('总页数有%s'%page_num.text)
    page_num=int(page_num.text)
    get_source(driverwait,int(num),driver)
    book.save(u'a.xlsx')
    print('*******finish*****')
    driver.quit()
def get_source(driverwait,page_num,driver):
    ccc=[]
  #page_num+1
    for i in range(1,page_num+1):
        
        time.sleep(1)
        get_content(driver)
        print('第%s页ing'%i)
        next_page(driverwait)

        
def next_page(driverwait):
    button=driverwait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#all-list > div.flow-loader > div.page-wrap > div > ul > li.page-item.next > button')))
    button.click()
def get_content(driver):
    html=driver.page_source
    selector=etree.HTML(html)
    list=selector.xpath('//div[@class="info"]')
    print(len(list))
    title=selector.xpath('//div[@class="info"]//a/@title')
    date=selector.xpath('//span[@class="so-icon time"]/text()')
    link=selector.xpath('//div[@class="headline clearfix"]/a/@href')
    link_space=selector.xpath('//span[@class="so-icon"]/a/@href')
    up=selector.xpath('//a[@class="up-name"]/text()')
    for i in range(0,20):
        global n
        sheet.write(n,0,title[i])
        sheet.write(n,1,date[i])
        sheet.write(n,2,link[i])
        sheet.write(n,3,link_space[i])
        sheet.write(n,4,up[i])
        n=n+1

    
    
        
    
    
  
    
main()
