from urllib.request import urlopen,Request
from urllib.error import HTTPError
from bs4 import BeautifulSoup
from urllib import request
import re
import pymssql
import _thread
import json
import time
import requests
import socks
import socket
import logging
import logging.handlers
import asyncio
import math
import ssl
from SqlServer import SQLServer


# 配置日志
# logging.basicConfig(filename="test.log",filemode="w",format="%(asctime)s-%(name)s-%(levelname)s-%(message)s",level=logging.DEBUG)
# logging 初始化工作
logging.basicConfig()

myapp = logging.getLogger('logger')
myapp.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s - %(message)s')

filehandler = logging.handlers.TimedRotatingFileHandler('test.log',when='D',interval=1,backupCount=3)
filehandler.suffix = "%Y-%m-%d.log"
filehandler.setFormatter(formatter)

consolehandler = logging.StreamHandler()
consolehandler.setFormatter(formatter)

myapp.addHandler(filehandler)
myapp.addHandler(consolehandler)

# # 连接数据库
# conn = pymssql.connect(server='127.0.0.1',user='invengolibrarytest',password='123456',database='ResourcesDB')
# cur = conn.cursor()
# if not cur:
#     raise NameError("数据库连接失败")
baseDb = SQLServer('119.23.70.224','invengolibrarytest','123456','ResourcesDB')

# 基础url和请求头
baseUrl = "http://www.openbookdata.com.cn"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
}
userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
proxies = None
session = requests.Session()

def run():
    row = 0
    countRes = baseDb.ExecQuery("select count(1) as count from resopenbook")
    myapp.info(countRes)
    count = countRes[0]["count"]
    # cur.execute("select count(1) as count from resopenbook") # 获取到图书信息的总数
    # count = cur.fetchone()['count']
    ssl._create_default_https_context = ssl._create_unverified_context
    while row<count:
        # print(row)
        try:
            data = baseDb.ExecQuery("select NewBookDecode,id from resopenbook where id>%d and id<=%d order by id",(row,row+100))
            # cur.execute("select NewBookDecode from resopenbook where id>%d and id<=%d and image is null",(row,row+100)) # 每次获取100条图书id
            # data = cur.fetchall()
            for rowData in data:  # 遍历图书信息
                # print(rowData)
                try:
                    rowid = rowData['id']
                    bookid = rowData['NewBookDecode']
                    myapp.info(rowid)
                    url = "http://www.openbookdata.com.cn/handlers/BookController/LoadMassDataByBookID.ashx?bookid=" + bookid
                    response = session.get(url,headers=headers)
                    resJson = json.loads(response.text)
                    AuthorIntroduction = resJson[0].get('AuthorIntroduction') if resJson[0].get('AuthorIntroduction')!='' else None
                    MarketingActivity = resJson[0].get('MarketingActivity') if resJson[0].get('MarketingActivity')!='' else None
                    Recommendation = resJson[0].get('Recommendation') if resJson[0].get('Recommendation')!='' else None
                    Catalogue = resJson[0].get('Catalogue') if resJson[0].get('Catalogue')!='' else None
                    ReaderGroup = resJson[0].get('ReaderGroup') if resJson[0].get('ReaderGroup')!='' else None
                    Sheet = resJson[0].get('Sheet') if resJson[0].get('Sheet')!='' else None
                    Language = resJson[0].get('Language') if resJson[0].get('Language')!='' else None
                    WordNum = resJson[0].get('WordNum') if resJson[0].get('WordNum')!='' else None
                    # myapp.info(AuthorIntroduction)
                    
                    try:
                        baseDb.ExecNonQuery("update resopenbook set AuthorIntroduction=%s,MarketingActivity=%s,Recommendation=%s,Catalogue=%s,ReaderGroup=%s,Sheet=%s,Language=%s,WordNum=%s where id=%s",(AuthorIntroduction,MarketingActivity,Recommendation,Catalogue,ReaderGroup,Sheet,Language,WordNum,rowid))
                    except Exception as err:
                        myapp.error("数据库更新失败：{0}".format(err))
                except Exception as err:
                    myapp.error("访问页面失败：{0}".format(err))
                    time.sleep(1)
                
        except Exception as err:
            myapp.info(row)
            myapp.error("该批次处理失败：{0}".format(err))
        row += 100

if __name__=='__main__':
    run()
