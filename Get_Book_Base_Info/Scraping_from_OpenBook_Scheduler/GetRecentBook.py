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
import datetime

class GetRecentBook:

    def __init__(self, recentDay=15, pageSize=50):
        # 配置日志
        # logging.basicConfig(filename="test.log",filemode="w",format="%(asctime)s-%(name)s-%(levelname)s-%(message)s",level=logging.DEBUG)
        # logging 初始化工作
        logging.basicConfig()

        self.myapp = logging.getLogger('logger')
        self.myapp.setLevel(logging.INFO)

        formatter = logging.Formatter('%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s - %(message)s')

        filehandler = logging.handlers.TimedRotatingFileHandler('test.log',when='D',interval=1,backupCount=3)
        filehandler.suffix = "%Y-%m-%d.log"
        filehandler.setFormatter(formatter)

        consolehandler = logging.StreamHandler()
        consolehandler.setFormatter(formatter)

        self.myapp.addHandler(filehandler)
        self.myapp.addHandler(consolehandler)

        # 连接数据库
        self.conn = pymssql.connect(server='119.23.70.224',user='invengolibrarytest',password='123456',database='ResourcesDB')
        self.cur = self.conn.cursor(as_dict=True)
        if not self.cur:
            raise NameError("数据库连接失败")

        # 基础url和请求头
        self.baseUrl = "http://opac.gzlib.gov.cn/opac/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
        }
        self.userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
        self.proxies = None
        self.session = requests.Session()

        # 配置访问近几天的数据
        self.recentDay = recentDay
        self.pageSize = pageSize



    def getProxy(self):
        try:
            proxy_support = request.ProxyHandler(proxies=None)
            opener = request.build_opener(proxy_support)
            opener.addheaders = [('User-agent', self.userAgent)]
            request.install_opener(opener)
            requestProxy = Request('http://127.0.0.1:5010/get/',headers=self.headers)
            proxyResponse = urlopen(requestProxy)
            proxyIp = proxyResponse.read().decode(encoding="utf8")
            return proxyIp
        except HTTPError as httperror:
            self.myapp.error("获取代理请求失败：{0}".format(httperror))
            return None
        except Exception as err:
            self.myapp.error("获取代理失败：{0}".format(err))
            return None

    def changeProxy(self):
        proxyIp = self.getProxy()
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

    def loginOpenBook(self):
        data = {'ln':'1529726299@qq.com','pw':'123456','ts':'1564190831351'}
        response = self.session.post('http://www.openbookdata.com.cn/handlers/UserController/UserLogins.ashx',data=data)
        print(response.text)

    def getInfoFromOpenBook(self,pageIndex,pageSize=50):
        try:
            # today = time.strftime("%Y-%m-%d", time.localtime())
            # lastWeak = time.strftime("%Y-%m-%d", time.localtime())
            now = datetime.datetime.now()
            today = datetime.date.today()
            offset = datetime.timedelta(days = -self.recentDay)
            lastWeak = (now + offset).strftime('%Y-%m-%d')
            response = self.session.get('http://www.openbookdata.com.cn/Templates/BookListTemplate.tt?_ver=636063318682891054&_orderindex=0&_ordertype=0&__mode=1&_pageIndex='+str(pageIndex)+'&_pageSize='+str(pageSize)+'&ts=1564190831351&showtype=1&title=&author=&pubname=&plotname=&publishsdate=&publishedate=&selShip=-1&starttime=' + str(lastWeak) + '&endtime=' + str(today) + '&chkispub=0&chkisrecommend=0&selkind=&kinds=C-1%252CT-1%252CI-1%252CH-1%252CW-1%252CY-1%252CG-1%252CZ-1%252C&pd=&st=&rurl=http%253A%2F%2Fwww.openbookdata.com.cn%2FBookSearch%2FBookList.aspx%253Fpr1%253D%2526pr2%253D%2526pr3%253D%2526pr4%253D%2526pr5%253D%2526pr5e%253D%2526pr6%253D-1%2526pr7%253D%2526pr8%253D%2526pr9%253D0%2526pr10%253D0%2526pr11%253D%2526pr12%253DC-1%252CT-1%252CI-1%252CH-1%252CW-1%252CY-1%252CG-1%252CZ-1%252C%2526pr23%253D%2526pr24%253D&pmin=&pmax=',headers=self.headers)
            resJson = json.loads(response.text)
            bookList = resJson.get('list')
            row = 0
            for book in bookList:
                BookID=book.get('BookID')
                self.cur.execute("select * from resopenbook where bookid=%s",(BookID,))
                bookdata = self.cur.fetchall()
                row += 1
                # print(len(bookdata))
                # time.sleep(0.5)
                if len(bookdata)>0:
                    print("{0}-{1}不插入,bookid:{2}".format(pageIndex,row,BookID))
                    continue
                print("{0}-{1}插入,bookid:{2}".format(pageIndex,row,BookID))
                ISBN=book.get('ISBN')
                Title=book.get('Title')
                Price=book.get('Price')
                Author=book.get('Author')
                Name=book.get('Name')
                DealerName=book.get('DealerName')
                PublishDate=book.get('PublishDate')
                InputDate=book.get('InputDate')
                ShipRemark=book.get('ShipRemark')
                Kind1=book.get('Kind1')
                Kind2=book.get('Kind2')
                Kind3=book.get('Kind3')
                Kind1Name=book.get('Kind1Name')
                Kind2Name=book.get('Kind2Name')
                Kind3Name=book.get('Kind3Name')
                RecommendLevel=book.get('RecommendLevel')
                ImgBID=book.get('ImgBID')
                ServerName=book.get('ServerName')
                initPath=book.get('initPath')
                CoverInputDate=book.get('CoverInputDate')
                FileName=book.get('FileName')
                Abstract=book.get('Abstract')
                IsImportant=book.get('IsImportant')
                PublishID=book.get('PublishID')
                DealerID=book.get('DealerID')
                NewBookDecode=book.get('NewBookDecode')
                imgUrl=book.get('imgUrl')
                EcodePubid=book.get('EcodePubid')
                EcodeDealerid=book.get('EcodeDealerid')
                self.cur.execute("insert into ResOpenBook (BookID,ISBN,Title,Price,Author,Name,DealerName,PublishDate,InputDate,ShipRemark,Kind1,Kind2,Kind3,Kind1Name,Kind2Name,Kind3Name,RecommendLevel,ImgBID,ServerName,initPath,CoverInputDate,FileName,Abstract,IsImportant,PublishID,DealerID,NewBookDecode,imgUrl,EcodePubid,EcodeDealerid) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(BookID,ISBN,Title,Price,Author,Name,DealerName,PublishDate,InputDate,ShipRemark,Kind1,Kind2,Kind3,Kind1Name,Kind2Name,Kind3Name,RecommendLevel,ImgBID,ServerName,initPath,CoverInputDate,FileName,Abstract,IsImportant,PublishID,DealerID,NewBookDecode,imgUrl,EcodePubid,EcodeDealerid))
                self.conn.commit()
        except HTTPError as httperror:
            self.myapp.error("页面网络请求失败：{0}".format(httperror))
            time.sleep(5)
            self.getInfoFromOpenBook(pageIndex)
        except OSError as oserror:
            self.myapp.error("系统出错：{0}".format(oserror))
            time.sleep(5)
            self.getInfoFromOpenBook(pageIndex)
        except Exception as err:
            self.myapp.error("处理页面失败:{0}".format(err))
        

    def run(self):
        self.loginOpenBook()
        now = datetime.datetime.now()
        today = datetime.date.today()
        offset = datetime.timedelta(days = -self.recentDay)
        lastWeak = (now + offset).strftime('%Y-%m-%d')
        response = self.session.get('http://www.openbookdata.com.cn/Templates/BookListTemplate.tt?_ver=636063318682891054&_orderindex=0&_ordertype=0&__mode=1&_pageIndex=1&_pageSize=10&ts=1564190831351&showtype=1&title=&author=&pubname=&plotname=&publishsdate=&publishedate=&selShip=-1&starttime=' + str(lastWeak) + '&endtime=' + str(today) + '&chkispub=0&chkisrecommend=0&selkind=&kinds=C-1%252CT-1%252CI-1%252CH-1%252CW-1%252CY-1%252CG-1%252CZ-1%252C&pd=&st=&rurl=http%253A%2F%2Fwww.openbookdata.com.cn%2FBookSearch%2FBookList.aspx%253Fpr1%253D%2526pr2%253D%2526pr3%253D%2526pr4%253D%2526pr5%253D%2526pr5e%253D%2526pr6%253D-1%2526pr7%253D%2526pr8%253D%2526pr9%253D0%2526pr10%253D0%2526pr11%253D%2526pr12%253DC-1%252CT-1%252CI-1%252CH-1%252CW-1%252CY-1%252CG-1%252CZ-1%252C%2526pr23%253D%2526pr24%253D&pmin=&pmax=',headers=self.headers)
        resJson = json.loads(response.text)
        count = resJson.get('cnt')
        pageCount = math.ceil(count / self.pageSize) + 1
        print(count)
        print(pageCount)
        # getInfoFromOpenBook(1)
        for pageIndex in range(1,pageCount):
            self.myapp.info(pageIndex)
            self.getInfoFromOpenBook(pageIndex,self.pageSize)

if __name__=='__main__':
    getRecentBook = GetRecentBook()
    getRecentBook.run()

