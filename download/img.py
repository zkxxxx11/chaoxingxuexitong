import os
import requests
from requests.adapters import HTTPAdapter
import os
import traceback
import csv
from collections import OrderedDict
def main():
    urls='http://ww4.sinaimg.cn/large/61ecce97ly1gbv0wewdtqj20ku32tgs2.jpg,http://ww3.sinaimg.cn/large/61ecce97ly1gbv0wev1kbj20ku2b7n1e.jpg,http://ww3.sinaimg.cn/large/61ecce97ly1gbv0weuagdj20ku1d5n09.jpg,http://ww2.sinaimg.cn/large/61ecce97ly1gbv0wevq9yj20ku1omdlu.jpg,http://ww1.sinaimg.cn/large/61ecce97ly1gbv0wev15sj20ku1ran0r.jpg,http://ww1.sinaimg.cn/large/61ecce97ly1gbv0wev9h4j20ku1kywhs.jpg,http://ww4.sinaimg.cn/large/61ecce97ly1gbv0wf2mj1j20ku18d76l.jpg,http://ww4.sinaimg.cn/large/61ecce97ly1gbv0wf3zi3j20ku1kyjuz.jpg,http://ww2.sinaimg.cn/large/61ecce97ly1gbv0wf4o0lj20ku1kyq6k.jpg'
    urls=urls.split(',')
    file_dir = os.path.split(
                    os.path.realpath(__file__)
                )[0]+ os.sep + 'img'
    if not os.path.isdir(file_dir):
            os.makedirs(file_dir)

    print(file_dir)
    for i , url in enumerate(urls):
        houzhui=url[url.rfind('.'):]
        file_name=str(i+1)+houzhui
        file_path=file_dir+os.sep + file_name
        print(file_name)
        print(file_path)
        s=requests.Session()
        s.mount(url,HTTPAdapter(max_retries=5))
        downloaded=s.get(url,timeout=(5,10))
        with open(file_path,'wb')as f:
            f.write(downloaded.content)
main()
