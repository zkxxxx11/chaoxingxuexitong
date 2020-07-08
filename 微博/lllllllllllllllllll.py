os.path.split()
os.path.realpath()
config_path=os.path.split(os.path.realpath(__file__))[0]+os.sep+'文件名'
if not os.path.isfile(config_path):
    sys.exit(u'当前路径：%s不存在json文件' % (os.path.split(os.path.realpath(__file__)) + os.sep))
with open(config_path) as f:
    config = json.loads(f.read())    #import json os
file_dir = os.path.split(os.path.realpath(__file__))[0] + os.sep + 'weibo' + os.sep + self.user['nickname']
file_path = file_dir + os.sep + self.user_config['user_id'] + '.' + type
if not os.path.isdir(file_dir):
    os.makedirs(file_dir)  文件夹

#from datetime import date, datetime, timedelta
str(date.today()-timedelta(2))-----'2020-07-01'
>>> datetime.now()
datetime.datetime(2020, 7, 4, 22, 18, 50, 227231)
>>> datetime.now().strftime('%Y-%m-%d %H:%M')
'2020-07-04 22:18'
datetime.now().strftime('%Y-%m-%d %H:%M')

user_config_list = [{
    'user_id': user_id,
    'since_date': self.since_date
} for user_id in user_id_list]
>>> ss=[1,2,3,4]
>>> aa=[x+1 for x in ss]
>>> aa
[2, 3, 4, 5]

<input name="mp" type="hidden" value="105">
page_num=int(selector.xpath('//input[@name="mp"]/@value')[0])
page_num=int(selector.xpath('//input[@name="mp"]')[0].attrib['value'])

#要是元素
str_time = info.xpath('div/span[@class="ct"]')
str_time = self.handle_garbled(str_time[0])
def handle_garbled(self, info):
    """处理乱码"""
    try:

        info = (info.xpath('string(.)').replace(u'\u200b', '').encode(
            sys.stdout.encoding, 'ignore').decode(sys.stdout.encoding))

        return info
    except Exception as e:
        print('Error: ', e)
        traceback.print_exc()

import time
from time import sleep
sleep()    time.sleep()

import csv
weibo=OrderedDict()
[OrderedDict([('id', 'J9X65gwqJ'), ('content', '【祝福考生！名人大咖为#高考祝福。 \xa0今天 16:04\xa0来自微博 weibo.com'), ('publish_time', '2020-07-06 16:04')])
weibo['id']=info.xpath('@id')[0][2:]
weibo['content']=self.get_weibo_content(info)
weibo['publish_time'] = self.get_publish_time(info)
[odict_values(['J9X65gwqJ', '【祝福考生！福。 \xa0[组图共9张]\xa0原图\xa0赞[70]\xa0转发[17]\ibo.com', '2020-07-06 16:04']),[....],[....]]
def write_csv(self, wrote_num):
    try:
        result_headers = [
            'id',
            'content',
            'publish_time',
        ]

        result_data = [w.values() for w in self.weibo[wrote_num:]]

        with open(self.get_filepath('csv'), 'a', encoding='utf-8-sig', newline='')as f:
            writer = csv.writer(f)
            if wrote_num == 0:
                writer.writerows([result_headers])
            writer.writerows(result_data)

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


