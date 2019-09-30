import requests
import base64
import pymongo
import requests
import json
import string
import logging
import logging.handlers
import time
import ssl
from urllib.request import urlopen,Request
from urllib.error import HTTPError
from urllib import request
from urllib.parse import quote
import urllib3.contrib.pyopenssl



# 配置日志
# logging.basicConfig(filename="test.log",filemode="w",format="%(asctime)s-%(name)s-%(levelname)s-%(message)s",level=logging.DEBUG)
# logging 初始化工作
logging.basicConfig()

myapp = logging.getLogger('logger')
myapp.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s - %(message)s')

filehandler = logging.handlers.TimedRotatingFileHandler('getbook.log',when='D',interval=1)
filehandler.suffix = "%Y-%m-%d.log"
filehandler.setFormatter(formatter)

consolehandler = logging.StreamHandler()
consolehandler.setFormatter(formatter)

myapp.addHandler(filehandler)
myapp.addHandler(consolehandler)

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
dblist = myclient.list_database_names()
# dblist = myclient.database_names() 
if "ResourcesDB" in dblist:
  print("数据库已存在！")

mydb = myclient["ResourcesDB"]

collist = mydb.list_collection_names()
# collist = mydb.collection_names()
if "ResDoubanBook" in collist:   # 判断 sites 集合是否存在
  print("集合已存在！")

resDoubanBook = mydb["ResDoubanBook"]
resDoubanBook.create_index([("id",1)], unique=True)

visitNum = 0
changeNum = 0


def base_code(username, password):
    str = '%s:%s' % (username, password)
    encodestr = base64.b64encode(str.encode('utf-8'))
    return '%s' % encodestr.decode() 

url = "https://api.douban.com/v2/book/3000001?apikey=0df993c66c0c636e29ecbb5344252a4a"

ip_port = '183.165.29.23:39828' # 从api中提取出来的代理IP:PORT
username = '1529726299@qq.com'
password = 'Cyy123456'

basic_pwd = base_code(username, password)

headers = {
    'Proxy-Authorization': 'Basic %s' % (base_code(username, password))
}

proxy = {
    'http' : 'socks5://{}'.format(ip_port),
    'https' : 'socks5://{}'.format(ip_port)
}

# session = requests.Session()

def changeIp():
    global changeNum
    url = "http://api.wandoudl.com/api/ip?app_key=1e17571a889de3574c02467b4d8c1cd8&pack=207451&num=1&xy=3&type=2&mr=1&"
    response = urlopen(url)
    resStr = response.read().decode("utf-8")
    # myapp.info("获取代理：{0}".format(resStr))
    resJson = json.loads(resStr)
    resCode = resJson.get("code")
    resMsg = resJson.get("msg")
    resData = resJson.get("data")
    # print(resCode)
    if resCode == 200:
        ip_port = resData[0].get("ip") + ":" + str(resData[0].get("port"))
        myapp.info("代理获取成功：{0}".format(ip_port))
        changeNum = 0
        return ip_port
    else:
        myapp.error("代理获取失败，失败代码：{0}，失败信息：{1}".format(resCode,resMsg))
        changeNum += 1
        if changeNum > 5:
            return None
        else:
            return changeIp()

def getbookbyid(id):
    global visitNum
    global proxy
    global headers
    if visitNum > 30:
        visitNum = 0
    if visitNum == 0:
        ip_proxy = changeIp()
        if ip_proxy != None:
            ip_port = ip_proxy
        
        proxy = {
            'http' : 'socks5://{}'.format(ip_port),
            'https' : 'socks5://{}'.format(ip_port)
        }
    # baseUrl = url
    # ssl._create_default_https_context = ssl._create_unverified_context
    # myapp.info(proxy)
    # myapp.info(headers)
    # urllib3.contrib.pyopenssl.inject_into_urllib3()
    baseUrl = "https://api.douban.com/v2/book/" + str(id) + "?apikey=0df993c66c0c636e29ecbb5344252a4a"
    # requests.packages.urllib3.disable_warnings()
    response = requests.get(baseUrl, proxies=proxy, headers=headers)
    # print(response.text)
    # print(visitNum)
    visitNum += 1
    resJson = json.loads(response.text)
    return resJson

def run():
    id = 3000345
    # print(proxy)
    # r = requests.get(url,proxies=proxy, headers=headers)
    # print(r.text)
    # myapp.info(headers)
    # baseUrl = "https://api.douban.com/v2/book/" + str(id) + "?apikey=0df993c66c0c636e29ecbb5344252a4a"
    # # requests.packages.urllib3.disable_warnings()
    # response = requests.get(baseUrl, proxies=proxy, headers=headers)
    # myapp.info(response.text)
    while True:
        try:
            # getbookbyid(id)
            resJson = getbookbyid(id)
            resCode = resJson.get("code")
            if resCode == None:
                # myapp.info(resJson)
                try:
                    resDoubanBook.insert(resJson)
                    myapp.info("id:{0}数据库插入成功")
                except Exception as err:
                    myapp.error("id:{0}数据库插入失败,错误信息：{1}".format(id,err))
        except Exception as err:
            myapp.error("id:{0}访问失败,错误信息：{1}".format(id,err))

        id += 1


if __name__=='__main__':
    run()