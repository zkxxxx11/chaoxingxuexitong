import urllib.request
import urllib.parse
import json
content=input('请输入内容：')
url='http://fanyi.youdao.com/translate?smartresult=dict&smartresult=rule'
data={}
data['i']=content
data['from']='AUTO'
data['to']='AUTO'
data['smartresult']='dict'
data['client']='fanyideskweb'
data['salt']='1519739039196'
data['sign']='dce281ee82f5b9111de24f0bcfa147f1'
data['doctype']='json'
data['version']='2.1'
data['keyfrom']='fanyi.web'
data['action']='FY_BY_REALTIME'
data['typoResult']='false'
data=urllib.parse.urlencode(data).encode('utf-8')

response=urllib.request.urlopen(url,data)

html=response.read().decode('utf-8')
print(html)
xx=json.loads(html)
print('out:',xx['translateResult'][0][0]['tgt'])
