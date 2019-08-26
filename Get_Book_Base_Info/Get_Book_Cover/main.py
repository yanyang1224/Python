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
import uuid
import ssl

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

# 连接数据库
conn = pymssql.connect(server='127.0.0.1',user='InvengoLibraryTest',password='123456',database='ResourcesDB')
cur = conn.cursor(as_dict=True) # 除了在建立连接时指定，还可以在这里指定as_dict=True
if not cur:
    raise NameError("数据库连接失败")

userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
proxies = None

def getProxy():
    try:
        proxy_support = request.ProxyHandler(proxies=None)
        opener = request.build_opener(proxy_support)
        opener.addheaders = [('User-agent', userAgent)]
        request.install_opener(opener)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'}
        requestProxy = Request('http://127.0.0.1:5010/get/',headers=headers)
        proxyResponse = urlopen(requestProxy)
        proxyIp = proxyResponse.read().decode(encoding="utf8")
        return proxyIp
    except HTTPError as httperror:
        myapp.error("获取代理请求失败：{0}".format(httperror))
        return None
    except Exception as err:
        myapp.error("获取代理失败：{0}".format(err))
        return None

def changeProxy():
    proxyIp = getProxy()
    # print(proxyIp)
    if proxyIp != None:
        proxies = {
            'http':'http://' + proxyIp
        }
    print(proxies)

def findImgFromDouban(isbn):
    # request = Request('http://book.douban.com/isbn/' + isbn,headers=headers)
    # html = urlopen(request)
    proxy_support = request.ProxyHandler(proxies)
    opener = request.build_opener(proxy_support)
    opener.addheaders = [('User-agent', userAgent)]
    request.install_opener(opener)
    html = request.urlopen('http://book.douban.com/isbn/' + isbn)
    bs = BeautifulSoup(html,'html.parser')
    imgUrl = bs.find('div',{'id':'mainpic'}).img.get('src')
    return imgUrl

def main():
    row = 44666
    cur.execute("select count(1) as count from resopenbook") # 获取到图书信息的总数
    count = cur.fetchone()['count']
    ssl._create_default_https_context = ssl._create_unverified_context
    while row<count:
        # print(row)
        try:
            cur.execute("select * from resopenbook where id>%d and id<=%d and image is null",(row,row+100)) # 每次获取100条图书信息
            data = cur.fetchall()
            for rowData in data:  # 遍历图书信息
                # print(rowData)
                isbn = rowData['ISBN']
                imgUrl = rowData['imgUrl']
                rowId = rowData['Id']
                guid = str(uuid.uuid1()).replace('-','')
                if isbn!=None:
                    try:
                        # changeProxy()  # 每次访问更改代理IP
                        # proxy_support = request.ProxyHandler(proxies)
                        # opener = request.build_opener(proxy_support)
                        # opener.addheaders = [('User-agent', userAgent)]
                        # request.install_opener(opener)
                        isbn = isbn.replace('-','')
                        url = 'https://pds.cceu.org.cn/cgi-bin/isbn_cover.cgi?isbn='+isbn+'&large=Y'
                        # print(isbn)
                        # print(guid)
                        # print(url)
                        myapp.info(rowId)
                        with urlopen(url) as response:
                            # print(response)
                            statusCode = response.status
                            fstream = response.read()
                            if statusCode==200 and len(fstream)>3000: # 如果请求正常且文件大小大于3k则存入文件并更新数据库
                                imgUrl = 'images/'+guid+'.png'
                                with open(imgUrl,'wb') as f_save:
                                    f_save.write(fstream)
                                    f_save.flush()
                                    f_save.close()
                                try:
                                    cur.execute("update resopenbook set image=%s where id=%s",(imgUrl,rowId))
                                    conn.commit()
                                except Exception as err:
                                    conn.rollback()
                            elif imgUrl!=None and re.match(r'^https?:\/\/(([a-zA-Z0-9_-])+(\.)?)*(:\d+)?(\/((\.)?(\?)?=?&?[a-zA-Z0-9_-](\?)?)*)*$',imgUrl,re.I):
                                with urlopen(imgUrl) as response:
                                    statusCode = response.status
                                    fstream = response.read()
                                    if statusCode==200 and len(fstream)>3000: # 如果请求正常且文件大小大于3k则存入文件并更新数据库
                                        imgUrl = 'images/'+guid+'.png'
                                        with open(imgUrl,'wb') as f_save:
                                            f_save.write(fstream)
                                            f_save.flush()
                                            f_save.close()
                                        try:
                                            cur.execute("update resopenbook set image=%s where id=%s",(imgUrl,rowId))
                                            conn.commit()
                                        except Exception as err:
                                            conn.rollback()
                                
                    except Exception as err:
                        myapp.error("该条处理失败：{0}".format(err))
                        # print(isbn)
                        # print(err)
        except Exception as err:
            myapp.info(row)
            myapp.error("该批次处理失败：{0}".format(err))
        row += 100
    print(count)

if __name__=='__main__':
    main()