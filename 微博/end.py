
import codecs
import copy
import csv
import json
import os
import random
import re
import sys
import traceback
from collections import OrderedDict
from datetime import date, datetime, timedelta
from time import sleep

import requests
from lxml import etree
from requests.adapters import HTTPAdapter
from tqdm import tqdm

class Weibo(object):
    def __init__(self, config):
        """Weibo类初始化"""
        self.filter = config['filter']
        since_date = str(config['since_date'])
        if since_date.isdigit():
            since_date=str(date.today()-timedelta(int(since_date)))
        self.since_date = since_date
        self.write_mode = config[
            'write_mode']  # 结果信息保存类型，为list形式，可包含txt、csv、json、mongo和mysql五种类型
        self.pic_download = config[
            'pic_download']  # 取值范围为0、1,程序默认值为0,代表不下载微博原始图片,1代表下载
        self.video_download = config[
            'video_download']  # 取值范围为0、1,程序默认为0,代表不下载微博视频,1代表下载
        self.cookie = {'Cookie': config['cookie']}
        user_id_list = config['user_id_list']
        user_config_list = [{
            'user_id': user_id,
            'since_date': self.since_date
        } for user_id in user_id_list]
        self.user_config_list = user_config_list  # 要爬取的微博用户的user_config列表
        self.user_config = {}  # 用户配置,包含用户id和since_date
        self.start_time = ''  # 获取用户第一条微博时的时间
        self.user = {}  # 存储爬取到的用户信息
        self.got_num = 0  # 存储爬取到的微博数
        self.weibo = []  # 存储爬取到的所有微博信息
        self.weibo_id_list = []  # 存储爬取到的所有微博id
    def get_nickname(self):
        url='https://weibo.cn/%s/info'%(self.user_config['user_id'])
        selector=self.handle_html(url)
        nickname=selector.xpath('//title/text()')[0]
        nickname = nickname[:-3]
        self.user['nickname']=nickname
    def get_page_num(self,selector):
        if selector.xpath("//input[@name='mp']")==[]:
            page_num=1
        else:
            page_num=(int)(selector.xpath("//input[@name='mp']")[0].attrib['value'])
            #page_num=selector.xpath("//input[@type='text']")[0].attrib['size']
        print(page_num)
        return page_num
    def print_user_info(self):
        
        """打印微博用户信息"""
        print(u'用户昵称: %s' % self.user['nickname'])
        print(u'用户id: %s' % self.user['id'])
        print(u'微博数: %d' % self.user['weibo_num'])
        print(u'关注数: %d' % self.user['following'])
        print(u'粉丝数: %d' % self.user['followers'])
    def get_user_info(self,selector):
        try:
            self.get_nickname()
            user_info=selector.xpath("//div[@class='tip2']/*/text()")

            print('::',user_info,len(user_info))

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
            print('Error: ', e)
            traceback.print_exc()

    def handle_garbled(self,info):
        """处理乱码"""
        try:
    
            info = (info.xpath('string(.)').replace(u'\u200b', '').encode(
                sys.stdout.encoding, 'ignore').decode(sys.stdout.encoding))
       
            return info
        except Exception as e:
            print('Error: ', e)
            traceback.print_exc()
        
    def get_original_weibo(self,info,weibo_id):
        try:
            weibo_content=self.handle_garbled(info)
            
            weibo_content=weibo_content[:weibo_content.rfind(u'赞')]
            a_text=info.xpath('div//a/text()')
        
            #if u'全文'in a_text:
                #weibo_link='https://weibo.cn/comment/' + weibo_id
            return weibo_content
        except Exception as e:
            print('Error: ', e)
            traceback.print_exc()
    def get_retweet(self,info,weibo_id):
        try:
            wb_content=self.handle_garbled(info)
            
            wb_content = wb_content[wb_content.find(':')+1:wb_content.rfind(u'赞')]
            wb_content = wb_content[:wb_content.rfind(u'赞')]
            
            return wb_content
        except Exception as e:
            print('Error: ', e)
            traceback.print_exc()
    def get_weibo_content(self,info,is_original):
        try:
            weibo_id=info.xpath('@id')[0][2:]
            if is_original:
                
                weibo_content=self.get_original_weibo(info,weibo_id)
                
            else:
                
                weibo_content=self.get_retweet(info,weibo_id)
                
            return weibo_content
        except Exception as e:
            print('Error: ', e)
            traceback.print_exc()            
    def is_original(self,info):
        is_original=info.xpath("div/span[@class='cmt']")
        if(len(is_original)>3):
            
            return False
        else:
           
            
            return True
    def extract_picture_urls(self,info,weibo_id):
        try:
            a_list=info.xpath('div/a/@href')
            first_pic = 'https://weibo.cn/mblog/pic/' + weibo_id + '?rl=0'
            all_pic = 'https://weibo.cn/mblog/picAll/' + weibo_id + '?rl=1'
            if first_pic in a_list:
                if all_pic in a_list:
                    selector=self.handle_html(all_pic)
                    preview_picture_list = selector.xpath('//img/@src')
                    picture_list = [
                        p.replace('/thumb180/', '/large/')
                        for p in preview_picture_list
                    ]
                    picture_urls = ','.join(picture_list)
                else:
                    if info.xpath('.//img/@src'):
                        preview_picture=info.xpath('.//img/@src')[-1]
                        
                        picture_urls = preview_picture.replace(
                            '/wap180/', '/large/')                        
                    else:
                        sys.exit(
                            u"爬虫微博可能被设置成了'不显示图片'，请前往"
                            u"'https://weibo.cn/account/customize/pic'，修改为'显示'"
                        )
            else:
                picture_urls = u'无'
            
            return picture_urls
        except Exception as e:
            print('Error: ', e)
            traceback.print_exc()
        
        
    def get_picture_urls(self,info,is_original):
        try:
            weibo_id=info.xpath('@id')[0][2:]
            picture_urls={}
            if is_original:
                original_pictures=self.extract_picture_urls(info,weibo_id)
                picture_urls['original_pictures'] = original_pictures
                if not self.filter:
                    picture_urls['retweet_pictures'] = u'无'
                
            else:
                retweet_url = info.xpath("div/a[@class='cc']/@href")[0]
                retweet_id = retweet_url.split('/')[-1].split('?')[0]
                retweet_pictures = self.extract_picture_urls(info, retweet_id)
                picture_urls['retweet_pictures'] = retweet_pictures
                a_list = info.xpath('div[last()]/a/@href')
                
                original_picture = u'无'
                for a in a_list:
                    if a.endswith(('.gif', '.jpeg', '.jpg', '.png')):
                        original_picture = a
                        break
                picture_urls['original_pictures'] = original_picture
            return picture_urls             
  
                
               
        except Exception as e:
            print('Error: ', e)
            traceback.print_exc()
    def get_video_url(self,info,is_original):
        try:
            if is_original:
                div_first=info.xpath('div')[0]
                a_list=div_first.xpath('.//a')
                video_link = u'无'
                for a in a_list:
                    if 'm.weibo.cn/s/video/show?object_id=' in a.xpath(
                            '@href')[0]:
                        video_link = a.xpath('@href')[0]
                        
                        break
                if video_link != u'无':
                    video_link = video_link.replace(
                        'm.weibo.cn/s/video/show', 'm.weibo.cn/s/video/object')
                    wb_info = requests.get(video_link,
                                           cookies=self.cookie).json()
                    video_url = wb_info['data']['object']['stream'].get(
                        'hd_url')
                    if not video_url:
                        video_url = wb_info['data']['object']['stream']['url']
                        if not video_url:  # 说明该视频为直播
                            video_url = u'无'
            else:
                video_url = u'无'
                
            return video_url
        except Exception as e:
            return u'无'
            print('Error: ', e)
            traceback.print_exc()
    def get_publish_place(self,info):
        try:
            div_first = info.xpath('div')[0]
            a_list = div_first.xpath('a')
            publish_place = u'无'
            for a in a_list:
                if ('place.weibo.com' in a.xpath('@href')[0]
                        and a.xpath('text()')[0] == u'显示地图'):
                    weibo_a = div_first.xpath("span[@class='ctt']/a")
                    if len(weibo_a) >= 1:
                        publish_place = weibo_a[-1]
                        if (u'视频' == div_first.xpath(
                                "span[@class='ctt']/a/text()")[-1][-2:]):
                            if len(weibo_a) >= 2:
                                publish_place = weibo_a[-2]
                            else:
                                publish_place = u'无'
                        publish_place = self.handle_garbled(publish_place)
                        break
            return publish_place
        except Exception as e:
            print('Error: ', e)
            traceback.print_exc()

    def get_publish_time(self,info):
        try:
            str_time=info.xpath("div/span[@class='ct']")

            str_time = self.handle_garbled(str_time[0])
            publish_time=str_time.split(u'来自')[0]
            
            if u'刚刚' in publish_time:
                publish_time = datetime.now().strftime('%Y-%m-%d %H:%M')
            elif u'分钟' in publish_time:
                minute = publish_time[:publish_time.find(u'分钟')]
                minute = timedelta(minutes=int(minute))
                publish_time = (datetime.now() -
                                minute).strftime('%Y-%m-%d %H:%M')
            elif u'今天' in publish_time:
                today = datetime.now().strftime('%Y-%m-%d')
                time = publish_time[3:]
                publish_time = today + ' ' + time
                if len(publish_time) > 16:
                    publish_time = publish_time[:16]
            elif u'月' in publish_time:
                year = datetime.now().strftime('%Y')
                
                month = publish_time[0:2]
                day = publish_time[3:5]
                time = publish_time[7:12]
                publish_time = year + '-' + month + '-' + day + ' ' + time
            else:
                publish_time = publish_time[:16]
            
            return publish_time


        except Exception as e:
            print('Error: ', e)
            traceback.print_exc()

            
    def get_publish_tool(self,info):
        try:
            str_time=info.xpath("div/span[@class='ct']")

            str_time = self.handle_garbled(str_time[0])
            if len(str_time.split(u'来自'))>1:

                publish_tool=str_time.split(u'来自')[1]
            else:
                publish_tool=u'无'

            return publish_tool

        except Exception as e:
            print('Error: ', e)
            traceback.print_exc()
    def get_weibo_footer(self,info):
        try:
            footer={}
            pattern=r'\d+'
   
            str_footer=info.xpath("div")[-1]
            str_footer = self.handle_garbled(str_footer)
            str_footer=str_footer[str_footer.rfind(u'赞['):]

            weibo_footer=re.findall(pattern,str_footer,re.M)

            up_num = int(weibo_footer[0])
            footer['up_num'] = up_num

            retweet_num = int(weibo_footer[1])
            footer['retweet_num'] = retweet_num

            comment_num = int(weibo_footer[2])
            footer['comment_num'] = comment_num
            
            return footer

        except Exception as e:
            print('Error: ', e)
            traceback.print_exc()

    def get_one_weibo(self,info):
        try:
            weibo=OrderedDict()
            is_original=self.is_original(info)
            if(not self.filter) or is_original:
                weibo['id']=info.xpath('@id')[0][2:]
               
                weibo['content']=self.get_weibo_content(info,is_original)
                picture_urls = self.get_picture_urls(info, is_original)
                weibo['original_pictures'] = picture_urls[
                    'original_pictures']  # 原创图片url
                if not self.filter:
                    weibo['retweet_pictures'] = picture_urls[
                        'retweet_pictures']  # 转发图片url
                    weibo['original'] = is_original  # 是否原创微博
                weibo['video_url'] = self.get_video_url(info,is_original)  # 微博视频url
                weibo['publish_place'] = self.get_publish_place(info)
                weibo['publish_time'] = self.get_publish_time(info)  # 微博发布时间
                weibo['publish_tool'] = self.get_publish_tool(info)  # 微博发布时间
                footer = self.get_weibo_footer(info)
                weibo['up_num']=footer['up_num']
                weibo['retweet_num'] = footer['retweet_num']  # 转发数
                weibo['comment_num'] = footer['comment_num']  # 评论数
            else:
                weibo = None
            return weibo


        except Exception as e:
            print('Error: ', e)
            traceback.print_exc()
    def str_to_time(self, text):
        """将字符串转换成时间类型"""
       
        if ':' in text:
            
            result = datetime.strptime(text, '%Y-%m-%d %H:%M')
        else:
            result = datetime.strptime(text, '%Y-%m-%d')
        return result
    def is_pinned_weibo(self, info):
        """判断微博是否为置顶微博"""
        kt = info.xpath(".//span[@class='kt']/text()")
        if kt and kt[0] == u'置顶':
            return True
        else:
            return False
    def print_one_weibo(self,weibo):
        print(weibo['content'])
        print(u'微博发布位置：%s' % weibo['publish_place'])
        print(u'发布发布时间：%s' % weibo['publish_time'])
        print(u'发布发布工具：%s' % weibo['publish_tool'])
        print(u'点赞数：%d' % weibo['up_num'])
        print(u'转发数：%d' % weibo['retweet_num'])
        print(u'评论数：%d' % weibo['comment_num'])

        

    def get_one_page(self,page):
        try:
            url='https://weibo.cn/u/%s?page=%d'%(self.user_config['user_id'],page)
            selector=self.handle_html(url)
            info=selector.xpath("//div[@class='c']")

            is_exist=info[0].xpath("div/span[@class='ctt']")

            if is_exist:
                for i in range(0,len(info)-2):
                    weibo=self.get_one_weibo(info[i])
                    
                    if weibo['id'] in self.weibo_id_list:
                        continue
                    
                    publish_time=self.str_to_time(weibo['publish_time'])
                    since_date=self.str_to_time(self.user_config['since_date'])
                    if publish_time<since_date:
                        if self.is_pinned_weibo(info[i]):
                            continue
                        else:
                            return True
                    self.print_one_weibo(weibo)
                    self.weibo.append(weibo)
                    self.weibo_id_list.append(weibo['id'])
                    self.got_num+=1
                    print('-'*100)
                        
                    
                    
                    
                    
                    
        except Exception as e:
            print('Error: ', e)
            traceback.print_exc()
    def get_filepath(self,type):
        try:
            file_dir = os.path.split(
                os.path.realpath(__file__)
            )[0] + os.sep + 'weibo' + os.sep + self.user['nickname']
            if type == 'img' or type == 'video':
                file_dir = file_dir + os.sep + type
                print('000000000'+file_dir)
            if not os.path.isdir(file_dir):
                os.makedirs(file_dir)
            if type == 'img' or type == 'video':
                return file_dir
            file_path = file_dir + os.sep + self.user_config[
                'user_id'] + '.' + type
            print(file_path)
            return file_path
        except Exception as e:
            print('Error: ', e)
            traceback.print_exc()
    def write_csv(self,wrote_num):
        """将爬取的信息写入csv文件"""
        try:
            result_headers = [
                '微博id',
                '微博正文',
                '原始图片url',
                '微博视频url',
                '发布位置',
                '发布时间',
                '发布工具',
                '点赞数',
                '转发数',
                '评论数',
            ]
            if not self.filter:
                result_headers.insert(3,'被转发微博原始图片url')
                result_headers.insert(4,'是否为原创微博')
            result_data=[w.values()for w in self.weibo[wrote_num:]]
            print('re da',result_data)
            if sys.version < '3':  # python2.x
                reload(sys)
                sys.setdefaultencoding('utf-8')
                with open(self.get_filepath('csv'), 'ab') as f:
                    f.write(codecs.BOM_UTF8)
                    writer = csv.writer(f)
                    if wrote_num == 0:
                        writer.writerows([result_headers])
                    writer.writerows(result_data)
            else:#python3
                with open(self.get_filepath('csv'),'a',encoding='utf-8-sig',newline='')as f:
                    writer=csv.writer(f)
                    if wrote_num==0:
                        writer.writerows([result_headers])
                    print(result_data)
                    writer.writerows(result_data)
            print(u'%d条微博写入csv文件完毕,保存路径:' % self.got_num)
            print(self.get_filepath('csv'))
        except Exception as e:
            print('Error: ', e)
            traceback.print_exc()
    def write_txt(self,wrote_num):
        try:
            temp_result=[]
            if wrote_num==0:
                if self.filter:
                    result_header=u'\n\n原创微博内容：\n'
                else:
                    result_header=u'\n\n微博内容：\n'
                result_header = (u'用户信息\n用户昵称：' + self.user['nickname'] +
                                 u'\n用户id: ' +
                                 str(self.user_config['user_id']) +
                                 u'\n微博数: ' + str(self.user['weibo_num']) +
                                 u'\n关注数: ' + str(self.user['following']) +
                                 u'\n粉丝数: ' + str(self.user['followers']) +
                                 result_header)
                temp_result.append(result_header)
            for i,w in enumerate(self.weibo[wrote_num:]):
                temp_result.append(
                    str(wrote_num + i + 1) + ':' + w['content'] + '\n' +
                    u'微博位置: ' + w['publish_place'] + '\n' + u'发布时间: ' +
                    w['publish_time'] + '\n' + u'点赞数: ' + str(w['up_num']) +
                    u'   转发数: ' + str(w['retweet_num']) + u'   评论数: ' +
                    str(w['comment_num']) + '\n' + u'发布工具: ' +
                    w['publish_tool'] + '\n\n')
            result=''.join(temp_result)
            with open(self.get_filepath('txt'),'ab')as f:
                f.write(result.encode(sys.stdout.encoding))
            print(u'%d条微博写入txt文件完毕,保存路径:' % self.got_num)
            print(self.get_filepath('txt'))
        except Exception as e:
            print('Error: ', e)
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
            with codecs.open(path,'r',encoding="utf-8")as f:
                data=json.load(f)
        weibo_info=self.weibo[wrote_num:]
        data=self.update_json_data(data,weibo_info)
        with codecs.open(path,'w',encoding="utf-8")as f:
            json.dump(data,f,ensure_ascii=False)
        print(u'%d条微博写入json文件完毕,保存路径:' % self.got_num)
        print(path)
        
        
    def write_data(self,wrote_num):
        if self.got_num > wrote_num:
            if 'csv' in self.write_mode:
                self.write_csv(wrote_num)
            if 'txt' in self.write_mode:
                self.write_txt(wrote_num)
            if 'json' in self.write_mode:
                self.write_json(wrote_num)
    def get_weibo_info(self):
        """获取微博信息"""
        try:
            url = 'https://weibo.cn/u/%s' % (self.user_config['user_id'])
            print(url)
            selector = self.handle_html(url)
            page_num = self.get_page_num(selector)
            print('num:',page_num)
            self.get_user_info(selector)  # 获取用户昵称、微博数、关注数、粉丝数
            page_num = self.get_page_num(selector)  # 获取微博总页数
            
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
                if page - page1==random_pages and page < page_num:
                    sleep(random.randint(6,10))
                    page1=page
                    random_pages=random.randint(1,5)
            
            self.write_data(wrote_num)
            if not self.filter:
                print(u'共爬取' + str(self.got_num) + u'条微博')
            else:
                print(u'共爬取' + str(self.got_num) + u'条原创微博')
        except Exception as e:
            print('Error: ', e)
            traceback.print_exc()

    def handle_html(self, url):
        """处理html"""
        try:

            html = requests.get(url, cookies=self.cookie).content

            selector = etree.HTML(html)
            return selector
        except Exception as e:
            print('Error: ', e)
            traceback.print_exc()
    def initialize_info(self, user_config):
        """初始化爬虫信息"""
        self.got_num = 0
        self.weibo = []
        self.user = {}
        self.user_config = user_config
        self.weibo_id_list = []
    def download_one_file(self,url,file_path,file_type,weibo_id):
        try:
            if not os.path.isfile(file_path):
                s=requests.Session()
                s.mount(url,HTTPAdapter(max_retries=5))
                downloaded=s.get(url,timeout=(5,10))
            
                with open(file_path,'wb')as f:
                    f.write(downloaded.content)
        except Exception as e:
            error_file = self.get_filepath(
                type) + os.sep + 'not_downloaded.txt'
            with open(error_file, 'ab') as f:
                url = weibo_id + ':' + url + '\n'
                f.write(url.encode(sys.stdout.encoding))
            print('Error: ', e)
            traceback.print_exc()
    def handle_download(self,file_type,file_dir,urls,w):
        print(w['publish_time'])
        file_prefix = w['publish_time'][:11].replace('-','')+'-'+w['id']
        print(file_prefix)
        print(urls)
        if file_type == 'img':
            if ',' in urls:
                print('dddd2')
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
                key='original_pictures'
            else:
                describe=u'视频'
                key='video_url'
            print(u'即将进行%s下载'%describe)
            file_dir=self.get_filepath(file_type)
            for w in tqdm(self.weibo,desc='Download progress'):
                print('w[key]',w[key])
                if w[key]!=u'无':
                    self.handle_download(file_type,file_dir,w[key],w)
            print(u'%s下载完毕,保存路径:' % describe)
            print(file_dir)
        except Exception as e:
            print('Error: ', e)
            traceback.print_exc()


    def start(self):
        try:
            for user_config in self.user_config_list:
                self.initialize_info(user_config)
                print('*' * 100)
                self.get_weibo_info()
                print(u'信息抓取完毕')
                print('*' * 100)

                if self.pic_download==1:
                    self.download_file('img')
                if self.video_download==1:
                    self.download_file('video')
        except Exception as e:
            print('Error: ', e)
            traceback.print_exc()



def main():
    try:
        config_path = os.path.split(
            os.path.realpath(__file__))[0] + os.sep + 'config.json'
        if not os.path.isfile(config_path):
            sys.exit(u'当前路径：%s 不存在配置文件config.json' %
                     (os.path.split(os.path.realpath(__file__))[0] + os.sep))
        with open(config_path) as f:
            config = json.loads(f.read())
        wb = Weibo(config)
        wb.start()  # 爬取微博信息
    except ValueError:
        print(u'config.json 格式不正确，请参考 '
              u'https://github.com/dataabc/weiboSpider#3程序设置')
    except Exception as e:
        print('Error: ', e)
        traceback.print_exc()

if __name__ == '__main__':
    main()
