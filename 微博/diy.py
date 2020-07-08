import traceback
import os
import csv
import sys
import json
from datetime import date, datetime, timedelta
import requests
from lxml import etree
import random
from tqdm import tqdm
from collections import OrderedDict
from time import sleep
from requests.adapters import HTTPAdapter
import codecs
class Weibo(object):
    def __init__(self,config):
        self.filter=config['filter']
        since_date=config['since_date']
        if since_date.isdigit():
            since_date=str(date.today()-timedelta(int(since_date)))
        self.since_date=since_date

        self.write_mode=config['write_mode']
        self.pic_download=config['pic_download']
        self.video_download=config['video_download']
        self.cookie={'Cookie':config['cookie']}
        user_id_list=config['user_id_list']
        user_config_list=[{
            'user_id':user_id,
            'since_date':self.since_date
        }for user_id in user_id_list]
        self.user_config_list=user_config_list
        print(user_config_list)
        self.user_config = {}  # 用户配置,包含用户id和since_date
        self.start_time = ''  # 获取用户第一条微博时的时间
        self.user = {}  # 存储爬取到的用户信息
        self.got_num = 0  # 存储爬取到的微博数
        self.weibo = []  # 存储爬取到的所有微博信息
        self.weibo_id_list = []  # 存储爬取到的所有微博id
    def initialize_info(self, user_config):
        """初始化爬虫信息"""
        self.got_num = 0
        self.weibo = []
        self.user = {}
        self.user_config = user_config

        self.weibo_id_list = []
    def handle_html(self,url):
        html=requests.get(url,cookies=self.cookie)
        selector=etree.HTML(html.content)
        return selector
    def get_page_num(self,selector):
        #page_num=int(selector.xpath('//input[@name="mp"]/@value')[0])
        page_num = int(selector.xpath('//input[@name="mp"]')[0].attrib['value'])

        return page_num

    def print_user_info(self):

        """打印微博用户信息"""
        print(u'用户昵称: %s' % self.user['nickname'])
        print(u'用户id: %s' % self.user['id'])
        print(u'微博数: %d' % self.user['weibo_num'])
        print(u'关注数: %d' % self.user['following'])
        print(u'粉丝数: %d' % self.user['followers'])
    def get_nikename(self):
        url='https://weibo.cn/%s/info'%(self.user_config['user_id'])
        selector=self.handle_html(url)
        nikename=selector.xpath('//title/text()')

        self.user['nickname']=nikename[0][:-3]
    def get_user_info(self,selector):
        try:
            self.get_nikename()
            user_info=selector.xpath('//div[@class="tip2"]/*/text()')
            weibo_num = int(user_info[0][3:-1])
            following = int(user_info[1][3:-1])
            followers = int(user_info[2][3:-1])
            self.user['weibo_num'] = weibo_num
            self.user['following'] = following
            self.user['followers'] = followers
            self.user['id'] = self.user_config['user_id']
            self.print_user_info()
            print('*' * 100)
        except Exception as e:
            print('error:',e)
            traceback.print_exc()

    def handle_garbled(self, info):
        """处理乱码"""
        try:

            info = (info.xpath('string(.)').replace(u'\u200b', '').encode(
                sys.stdout.encoding, 'ignore').decode(sys.stdout.encoding))

            return info
        except Exception as e:
            print('Error: ', e)
            traceback.print_exc()

    def get_weibo_content(self,info):
        try:
            weibo_id=info.xpath('@id')[0][2:]
            wb_content=self.handle_garbled(info)
            return wb_content
        except Exception as e:
            print('error:',e)
            traceback.print_exc()
    def extract_picture_urls(self,info,weibo_id):
        try:
            a_list=info.xpath('div/a/@href')
            first_pic='https://weibo.cn/mblog/pic/'+weibo_id+'?rl=0'
            all_pic = 'https://weibo.cn/mblog/picAll/' + weibo_id + '?rl=1'
            selector=self.handle_html(all_pic)
            pictures=selector.xpath('//div[@class="c"]/a/img/@src')
            pictures=','.join(pictures)
            print('??', type(pictures))
            return pictures
        except Exception as e:
            print('error:',e)
            traceback.print_exc()
    def get_img_url(self, info):
        weibo_id=info.xpath('@id')[0][2:]

        picture_urls={}
        url = self.extract_picture_urls(info,weibo_id)
        picture_urls['1']=url

        if url==[]:
            return None


        return picture_urls
    def get_publish_time(self,info):
        try:
            str_time=info.xpath('div/span[@class="ct"]')
            str_time=self.handle_garbled(str_time[0])

            if u'月' in str_time:
                year=datetime.now().strftime('%Y')
                month=str_time[0:2]
                day=str_time[3:5]
                hm=str_time[7:12]

                str_time=year+'-'+month+'-'+day+' '+hm
            elif u'分钟' in str_time:
                minute = str_time[:str_time.find(u'分钟')]
                minute = timedelta(minutes=int(minute))
                str_time = (datetime.now() -
                                minute).strftime('%Y-%m-%d %H:%M')
            elif u'今天' in str_time:
                today=datetime.now().strftime('%Y-%m-%d')
                time=str_time[3:8]
                str_time=today+' '+time





            return str_time
        except Exception as e:
            print('error:',e)
            traceback.print_exc()

    def get_one_weibo(self,info):
        try:
            weibo=OrderedDict()
            #is_original=self.is_original(info)
            if (not self.filter):

                weibo['id']=info.xpath('@id')[0][2:]
                weibo['content']=self.get_weibo_content(info)
                weibo['publish_time'] = self.get_publish_time(info)
                picture_urls=self.get_img_url(info)


                weibo['img_url']=picture_urls['1']

            else:
                weibo=None
                print('22222222222222222')
            return weibo
        except Exception as e:
            print('error:',e)
            traceback.print_exc()
    def str_to_time(self,text):
        """将字符串转换成时间类型"""

        if ':' in text:
            result=datetime.strptime(text,'%Y-%m-%d %H:%M')
        else:
            result = datetime.strptime(text, '%Y-%m-%d')
        return result
    def is_pinned_weibo(self,info):
        """判断微博是否为置顶微博"""
        kt = info.xpath(".//span[@class='kt']/text()")
        if kt and kt[0] == u'置顶':
            return True
        else:
            return False
    def get_one_page(self,page):
        url='https://weibo.cn/u/%s?page=%d'%(self.user_config['user_id'],page)
        selector=self.handle_html(url)
        info=selector.xpath('//div[@class="c"]')
        is_exist=info[0].xpath("div/span[@class='ctt']")
        if is_exist:
            for i in range(0,len(info)-2):
                weibo=self.get_one_weibo(info[i])
                if weibo['id'] in self.weibo_id_list:
                    continue
                publish_time = self.str_to_time(weibo['publish_time'])
                since_date = self.str_to_time(self.user_config['since_date'])
                if publish_time<since_date:
                    if self.is_pinned_weibo(info[i]):
                        continue
                    else:
                        return True
                self.print_one_weibo(weibo)
                self.weibo.append((weibo))
                self.weibo_id_list.append(weibo['id'])
                self.got_num+=1

        print('nextpage-----------------------------------------------')

    def print_one_weibo(self,weibo):
        print(weibo['content'])
        print(weibo['publish_time'])

    def get_weibo_info(self):
        try:
            url= 'https://weibo.cn/u/%s' % (self.user_config['user_id'])
            print(url)
            selector=self.handle_html(url)
            page_num=self.get_page_num(selector)

            self.get_user_info(selector)
            wrote_num=0
            page1=0
            random_pages=random.randint(1,5)
            self.start_time=datetime.now().strftime('%Y-%m-%d %H:%M')
            for page in tqdm(range(1,page_num+1),desc='Progress'):
                is_end=self.get_one_page(page)
                if is_end:
                    break
                if page%20==0:
                    self.write_date(wrote_num)
                    wrote_num=self.got_num
                if page-page1==random_pages and page<page_num:
                    sleep(random.randint(6,10))
                    page1=page
                    random_pages=random.randint(1,5)
            self.write_data(wrote_num)
        except Exception as e:
            print('error:',e)
            traceback.print_exc()
    def write_data(self,wrote_num):
        if self.got_num>wrote_num:
            if 'csv' in self.write_mode:
                self.write_csv(wrote_num)
            if 'txt' in self.write_mode:
                self.write_txt(wrote_num)
            if 'json' in self.write_mode:
                self.write_json(wrote_num)
    def get_filepath(self,type):
        try:

            file_dir=os.path.split(os.path.realpath(__file__))[0]+os.sep+'weibo'+os.sep+self.user['nickname']
            file_path=file_dir+os.sep+self.user_config['user_id']+'.'+type
            if type=='img' or type=='video':
                file_dir=file_dir+os.sep+type
            if not os.path.isdir(file_dir):
                os.makedirs(file_dir)
            if type=='img' or type=='video':

                return file_dir
            return file_path

        except Exception as e:
            print('error:', e)
            traceback.print_exc()
    def update_json_data(self, data, weibo_info):
        """更新要写入json结果文件中的数据，已经存在于json中的信息更新为最新值，不存在的信息添加到data中"""
        data['user'] = self.user
        if data.get('weibo'):
            is_new = 1  # 待写入微博是否全部为新微博，即待写入微博与json中的数据不重复
            for old in data['weibo']:
                if weibo_info[-1]['id'] == old['id']:
                    is_new = 0
                    break
            if is_new == 0:
                for new in weibo_info:
                    flag = 1
                    for i, old in enumerate(data['weibo']):
                        if new['id'] == old['id']:
                            data['weibo'][i] = new
                            flag = 0
                            break
                    if flag:
                        data['weibo'].append(new)
            else:
                data['weibo'] += weibo_info
        else:
            data['weibo'] = weibo_info
        return data
    def write_json(self,wrote_num):
        data={}
        path=self.get_filepath('json')
        if os.path.isfile(path):
            with codecs.open(path,'r',encoding='utf-8')as f:
                data=json.load(f)
        weibo_info=self.weibo[wrote_num:]
        data=self.update_json_data(data,weibo_info)
        with codecs.open(path,'w',encoding='utf-8')as f:
            json.dump(data,f,ensure_ascii=False)
        print(u'%d条微博写入json文件完毕,保存路径:' % self.got_num)
        print(path)
    def write_txt(self,wrote_num):
        try:
            temp_result=[]
            result_header=u'\n\n::::\n'
            temp_result.append(result_header)
            for i,w in enumerate(self.weibo[wrote_num:]):
                temp_result.append(str(wrote_num+i+1)+':'+w['content']+'\n'+
                                   u'id:'+w['id']+'\n'+u'publish:'+w['publish_time']+'\n\n')
                result=''.join(temp_result)
            with open(self.get_filepath('txt'),'ab')as f:
                f.write(result.encode(sys.stdout.encoding))
            print(u'%d条微博写入txt文件完毕,保存路径:' % self.got_num)
            print(self.get_filepath('txt'))

        except Exception as e:
            print('error:',e)
            traceback.print_exc()
    def write_csv(self,wrote_num):
        try:
            result_headers=[
                'id',
                'content',
                'publish_time',
            ]

            result_data=[w.values()for w in self.weibo[wrote_num:]]
            print('re da', self.weibo)
            with open(self.get_filepath('csv'),'a',encoding='utf-8-sig',newline='')as f:
                writer=csv.writer(f)
                if wrote_num==0:
                    writer.writerows([result_headers])
                writer.writerows(result_data)
            print(u'%d条微博写入csv文件完毕,保存路径:'% self.got_num)
            print(self.get_filepath('csv'))

        except Exception as e:
            print('error:',e)
            traceback.print_exc()
    def download_one_file(self,url,file_path,file_type,weibo_id):
        s=requests.Session()

        s.mount(url,HTTPAdapter(max_retries=5))
        downloaded=s.get(url,timeout=(5,10))
        with open(file_path,'wb')as f:
            f.write(downloaded.content)
    def handle_download(self,file_type,file_dir,urls,w):

        file_prefix = w['publish_time'][:11].replace('-','')+'-'+w['id']

        if file_type == 'img':
            if ',' in urls:

                url_list = urls.split(',')
                for i, url in enumerate(url_list):
                    file_suffix = url[url.rfind('.'):]
                    file_name = file_prefix + '_' + str(i + 1) + file_suffix
                    file_path = file_dir + os.sep + file_name
                    self.download_one_file(url, file_path, file_type, w['id'])
            else:
                print('dddddddddd3')
                file_suffix = url[url.rfind('.'):]
                file_name = file_prefix+ file_suffix
                file_path = file_dir + os.sep + file_name
                self.download_one_file(url, file_path, file_type, w['id'])
    def download_file(self,file_type):
        try:
            if file_type=='img':
                describe=u'图片'
                key='img_url'
            else:
                describe=u'视频'
                key='video_url'
            print(u'下载：%s'%describe)
            file_dir=self.get_filepath(file_type)
            for w in tqdm(self.weibo,desc='Download progress'):
                print('w[key]',w[key])
                if w[key]!='':

                    self.handle_download(file_type,file_dir,w[key],w)
            print(u'%s下载完毕,保存路径:' % describe)
            print(file_dir)
        except Exception as e:
            print('error:',e)
            traceback.print_exc()
    def start(self):
        try:
            for user_config in self.user_config_list:
                self.initialize_info(user_config)
                print('*' * 100)
                self.get_weibo_info()
                print('got_num:',self.got_num)
                print(u'finish')
                print('*' * 100)
            if self.pic_download==1:
                self.download_file('img')
        except Exception as e:
            print('error:',e)
            traceback.print_exc()

def main():
    try:
        config_path = os.path.split(
            os.path.realpath(__file__))[0] + os.sep + 'config.json'
        if not os.path.isfile(config_path):
            sys.exit(u'当前路径：%s不存在json'%(os.path.split(os.path.realpath(__file__))+os.sep))
        with open (config_path) as f:
            config=json.loads(f.read())
        wb=Weibo(config)
        wb.start()
    except ValueError:
        print('wrong')
    except Exception as e:
        print('error:',e)
        traceback.print_exc()
if __name__ == '__main__':
    main()
