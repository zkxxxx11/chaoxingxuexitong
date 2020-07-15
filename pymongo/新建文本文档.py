import pymongo
myclient=pymongo.MongoClient("mongodb://localhost:27017/")
mydb=myclient['douban']
mycol=mydb['dddd']
x=mycol.find({},{'score':{'$slice':1},{'score':0}})
n=0
for r in x:

    print(r)
    n+=1
print(n)