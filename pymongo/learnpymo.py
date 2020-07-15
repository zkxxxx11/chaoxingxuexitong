import pymongo
myclient=pymongo.MongoClient("mongodb://localhost:27017/")
mydb=myclient['rrrr']
mycol=mydb['sites']
mydict={'_id':1',1':'111','2':'222','3':'222222'}
#插入
x=mycol.insert_one(mydict)
x=mycol.insert_many([{'111':'22222','222':'3333'},{},{}])
#查找
x=mycol.find_one({})

x=mycol.find()
for x in mycol.find({'_id':1},{'_id':0,'111':1}):  0,1显示{}参数
    print(x)

myquery = { "name": { "$gt": "H" } } 第一个字母 ASCII 值大于 "H"
myquery = { "name": { "$regex": "^R" } }第一个字母为 "R" 的数据，正则表达式修饰符条件
x=mycol.find(myquery).limit(3)
x=mycol.find({'score':{'$exists':True}})存在score
mycol.find({$and:[{name:"python"},{age:50}]})
mycol.find({$or:[{name:"python"},{name:"android"}]})

x=mycol.find({'title':{'$in':['肖申克的救赎','霸王别姬']}})或
x=mycol.find({'title':{'$nin':['肖申克的救赎','霸王别姬']}})或
mycol.find({'age':{'$mod':[5,0]}})     $mod数字模操作{'age': {'$mod': [5, 0]}}年龄模5余0
# and与or联合使用.相当于 where age=18 and (name="python" or name="android")
db.Student.find({age:18,$or:[{name:"python"},{name:"android"}]})
# $nor语法,搜索name既不等于"python"且不等于"android"的所有数据
db.Student.find({"$nor":[{name:"python"},{name:"android"}]})
x=mycol.find({'title':{'$size':8}})# $size语法,查询info数组长度为8的所有数据['1',2,3]

db.Student.find({},{info:{$slice:-3}})# $slice语法，过滤，info数组中的后3个数据
# $where语法，搜索age=info的所有数据
db.Student.find({"$where":"this.age==this.info"})



修改
myquery={'111':'111'}
new={'$set':{'111':'121'}}
new2={'$set':{'1111':'1111'}}未有1111则添加
mycol.update_one(myquery,new)
myquery = { "name": { "$regex": "^F" } }
mycol.update_many(myquery,new)

排序
mydoc=mycol.find().sort('2',-1)'2'值降序 不改变内部

x=mycol.find().sort('score').skip(5)
print([r['score'] for r in x])

for x in mydoc:
    print(x)
results=mycol.find().sort('2')
print([results['2']for result in results])
xx=mycol.find().sort('2').skip(3).limit(3)忽略  限制
find({'_id': {'$gt': ObjectId('593278c815c2602678bb2b8d')}}) 这样的方法来查询，记录好上次查询的_id。
删除
mycol.delete_one({'1':'1'})
myquery = { "name": {"$regex": "^F"} }
mycol.delete_many(myquery)
mycol.delete_many({})
mycol.drop()

count=mycol.find({'2':2}).count()

字典
dict={'1':'1','2':'2'}
dict['3333']=dict.pop('1')
{'2': '2', '3333': '1'}