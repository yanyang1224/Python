from urllib.request import urlopen,Request
from urllib.error import HTTPError
import os,stat
import pymssql

# 连接数据库
conn = pymssql.connect(server='127.0.0.1',user='sa',password='123456',database='ResourcesDB')
# cur = conn.cursor()
cur = conn.cursor(as_dict=True) # 除了在建立连接时指定，还可以在这里指定as_dict=True
if not cur:
    raise NameError("数据库连接失败")

# 读取数据库中image数据，并将其存储为本地图片
cur.execute("select top 10 * from resbookinfo order by id asc")
# for row in cur:
#     print(row)
# 获取一条数据，还可以使用fetchmany和fetchall来一次性获取指定数量或者所有结果
data = cur.fetchone()
manyData = cur.fetchmany(2)
print(data)
print(manyData)

# print(data)
# with open('test1.jpg','wb') as f_save:
#     f_save.write(data[0])
#     f_save.flush()
#     f_save.close()

# # 读取图片并存储到数据库
# response = urlopen('https://pds.cceu.org.cn/cgi-bin/isbn_cover.cgi?isbn=9787115428523&large=Y')
# imgData = response.read()
# print(response)
# print(imgData)
# cur.execute("insert into ResBookInfo (image) values (%s)",(imgData))
# conn.commit()
# print('上传成功')

# # 将图片存储到本地
# with urlopen('https://pds.cceu.org.cn/cgi-bin/isbn_cover.cgi?isbn=9787115428523&large=Y') as response,open('test.jpg','wb') as f_save:
#     f_save.write(response.read())
#     f_save.flush()
#     f_save.close()

while 1:
    pass