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
conn = pymssql.connect(server='127.0.0.1',user='sa',password='123456',database='ResourcesDB')
cur = conn.cursor()
if not cur:
    raise NameError("数据库连接失败")

# 基础url和请求头
baseUrl = "http://opac.gzlib.gov.cn/opac/"
# headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'}
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
    # proxy_support = request.ProxyHandler(proxies)
    # opener = request.build_opener(proxy_support)
    # opener.addheaders = [('User-agent', userAgent)]
    # request.install_opener(opener)
    # time.sleep(5)

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

def findImgFromApi(isbn):
    # request = Request("https://book-resource.dataesb.com/websearch/metares?glc=P1ZJ0571017&cmdACT=getImages&type=0&isbns=," + isbn.replace("-","") + "&callback=showCovers&jsoncallback=jQuery16203261124622799938_1563010575439&_=1563010577413",headers=headers)
    # response = urlopen(request)
    proxy_support = request.ProxyHandler(proxies)
    opener = request.build_opener(proxy_support)
    opener.addheaders = [('User-agent', userAgent)]
    request.install_opener(opener)
    response = request.urlopen("https://book-resource.dataesb.com/websearch/metares?glc=P1ZJ0571017&cmdACT=getImages&type=0&isbns=," + isbn.replace("-","") + "&callback=showCovers&jsoncallback=jQuery16203261124622799938_1563010575439&_=1563010577413")
    responseBytes = response.readline()
    responseStr = responseBytes.decode(encoding="utf8")
    responseJson = json.loads(responseStr.replace("showCovers(","").replace(")",""))
    result = responseJson.get("result")
    if len(result)==0:
        return None
    else:
        return result[0].get("coverlink")

async def dealPage(url):
    try:
        # insidePage = Request(url,headers=headers)
        # inPageHtml = urlopen(insidePage)
        proxy_support = request.ProxyHandler(proxies)
        opener = request.build_opener(proxy_support)
        opener.addheaders = [('User-agent', userAgent)]
        request.install_opener(opener)
        inPageHtml = request.urlopen(url)
        bsInPage = BeautifulSoup(inPageHtml,'html.parser')
        bookTitle = bsInPage.find('table',{'id':'bookInfoTable'}).h2.get_text()
        bookIsbn = bsInPage.find('img',{'id':'bookcover_img'}).get('isbn')
        bookMarc = bsInPage.find('div',{'id':'bookMarcDiv'}).pre.get_text().replace('\u0000', '').replace('\x00', '')
        bookCover = None
        try:
            if(bookIsbn != ""):
                bookCover = findImgFromApi(bookIsbn)
        except:
            pass
        timeStr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        cur.execute("insert into ResBookInfoTest (PageUrl,Title,Isbn,ImgUrl,Marc,CreateTime) values (%s,%s,%s,%s,%s,%s)",(url,bookTitle,bookIsbn,bookCover,bookMarc,timeStr))
        conn.commit()
        # print(bookTitle)
        # print(bookIsbn)
        # print(bookMarc)
        # if(bookCover != None):
        #     print(bookCover)
    except HTTPError as httperror:
        myapp.info(url)
        myapp.error("内页网络请求失败：{0}".format(httperror))
    except Exception as err:
        myapp.info(url)
        myapp.error("处理内页失败:{0}".format(err))

def dealMainPage(page):
    try:
        changeProxy()
        mainUrl = baseUrl + "search?q=*%3A*&searchType=standard&isFacet=false&view=simple&searchWay=class&rows=1000&sortWay=score&sortOrder=desc&searchWay0=marc&logical0=AND&page=" + str(page)
        print(mainUrl)
        # request = Request(mainUrl,headers=headers)
        # html = urlopen(request)
        proxy_support = request.ProxyHandler(proxies)
        opener = request.build_opener(proxy_support)
        opener.addheaders = [('User-agent', userAgent)]
        request.install_opener(opener)
        html = request.urlopen(mainUrl)
        bs = BeautifulSoup(html,'html.parser')
        links = bs.find_all('span',{'class':'bookmetaTitle'}) #.find_all('a',href=re.compile(r'^(book\/)(\d+)$'))
        # print(len(links))
        # for link in links:
        #     # _thread.start_new_thread(dealPage,(baseUrl + link.a.get('href'),))
        #     # dealPage(baseUrl + link.a.get('href'))
        #     cor = dealPage(baseUrl + link.a.get('href'))
        #     task = asyncio.ensure_future(cor)
        #     loop = asyncio.get_event_loop()
        #     loop.run_until_complete(cor)
        tasks = [asyncio.ensure_future(dealPage(baseUrl + link.a.get('href'))) for link in links]
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait(tasks))
    except HTTPError as httperror:
        myapp.info(mainUrl)
        myapp.error("主页面网络请求失败：{0}".format(httperror))
        time.sleep(5)
        dealMainPage(page)
    except Exception as err:
        myapp.info(mainUrl)
        myapp.error("处理主页面失败:{0}".format(err))



for page in range(27,500,1):
    dealMainPage(page)
conn.close()
while 1:
    # getProxy()
    pass
    
    


