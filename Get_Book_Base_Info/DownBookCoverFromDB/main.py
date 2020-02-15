from urllib.request import urlopen,Request
from urllib.error import HTTPError
from bs4 import BeautifulSoup
from urllib import request
from urllib.parse import urlparse
import pymongo
import os
import re
import _thread
import json
import time
import requests
import socks
import socket
import logging
import logging.handlers
import asyncio
import aiohttp
import uuid
import ssl

# 配置日志
# logging.basicConfig(filename="test.log",filemode="w",format="%(asctime)s-%(name)s-%(levelname)s-%(message)s",level=logging.DEBUG)
# logging 初始化工作
logging.basicConfig()

myapp = logging.getLogger('logger')
myapp.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s - %(message)s')

filehandler = logging.handlers.TimedRotatingFileHandler('test.log',when='h',interval=1,encoding='utf-8')
filehandler.suffix = "%Y-%m-%d.log"
filehandler.setFormatter(formatter)

consolehandler = logging.StreamHandler()
consolehandler.setFormatter(formatter)

myapp.addHandler(filehandler)
myapp.addHandler(consolehandler)

headers = {
    'User-Agent':'Mozilla/5.0.html (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.html.2171.71 Safari/537.36'
}

myclient = pymongo.MongoClient("mongodb://119.23.70.224:27017/")
dblist = myclient.list_database_names()
# dblist = myclient.database_names() 
if "ResourcesDB" in dblist:
  myapp.info("ResourcesDB数据库已存在！")

mydb = myclient["ResourcesDB"]

collist = mydb.list_collection_names()
# collist = mydb.collection_names()
if "ResDoubanBook" in collist:   # 判断 sites 集合是否存在
  myapp.info("ResDoubanBook集合已存在！")

resDoubanBook = mydb["ResDoubanBook"]
resDoubanBook.create_index([("id",1)], unique=True)

def getbooks(startValue,pageSize):
    myapp.info("startValue:%d" % startValue)
    myapp.info("pageSize:%d" % pageSize)
    return resDoubanBook.find().limit(pageSize).skip(startValue)

async def downImg(url):
    try:
        if url!=None and re.match(r'^https?:\/\/(([a-zA-Z0-9_-])+(\.)?)*(:\d+)?(\/((\.)?(\?)?=?&?[a-zA-Z0-9_-](\?)?)*)*$',url,re.I):
            myapp.info("%s:尝试下载" % url)
            timeout = aiohttp.ClientTimeout(total=60)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    statusCode = response.status
                    fstream = await response.read()
                    if statusCode==200 : # 如果请求正常且文件大小大于3k则存入文件并更新数据库(暂时去掉限制)
                        imgPath = urlparse(url).path[1:]
                        dirPath = os.path.dirname(imgPath)
                        if not os.path.exists(dirPath):
                            os.makedirs(dirPath)
                        with open(imgPath,'wb') as f_save:
                            f_save.write(fstream)
                            f_save.flush()
                            f_save.close()
                            myapp.info("%s:下载完毕" % url)
                    else:
                        myapp.info("Http请求返回状态码：%d,url:%s" % (statusCode,url))
        else:
            myapp.info("%s:不是合理的url" % url)
    except Exception as err:
        myapp.error("该条处理失败：{0}".format(err))

async def control_sem(sem,url):
    async with sem:
        await downImg(url)

def run(data):
    loop = asyncio.get_event_loop()
    sem = asyncio.Semaphore(300)
    tasks = []
    for rowData in data:  # 遍历图书信息
        objectId = rowData['_id']
        myapp.info("当前id为：%s" % objectId)
        images = rowData['images']
        task1 = asyncio.ensure_future(control_sem(sem,images['medium']))
        task2 = asyncio.ensure_future(control_sem(sem,images['large']))
        task3 = asyncio.ensure_future(control_sem(sem,images['small']))
        tasks.append(task1)
        tasks.append(task2)
        tasks.append(task3)
    loop.run_until_complete(asyncio.wait(tasks))
    

if __name__=='__main__':
    row = 409500
    count = resDoubanBook.count_documents({})
    ssl._create_default_https_context = ssl._create_unverified_context
    myapp.info("图书总量为：%d" % count)
    while row<count:
        myapp.info("当前批次为：%d" % row)
        try: 
            data = getbooks(row,100)
            run(data)
            row += 100
        except Exception as err:
            myapp.error("该批次处理失败：{0}".format(err))