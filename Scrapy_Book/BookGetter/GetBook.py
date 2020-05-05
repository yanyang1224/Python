import aiohttp
import asyncio
import ssl
import json
import datetime
import time
import uuid
import sys
import os
import re
import requests
import pymongo
from bs4 import BeautifulSoup,Comment
from urllib.request import urlopen,Request
from urllib.error import HTTPError
from urllib import request
from urllib.parse import urlparse
from datetime import datetime

rootPath = os.path.abspath('../')
sys.path.append(rootPath)
from Util.LogHandler import LogHandler
from Util.MSSQLHelper import MSSQLHelper

myapp = LogHandler('test')
mssql = MSSQLHelper('127.0.0.1','sa','123456','ResourcesDB')

myclient = pymongo.MongoClient("mongodb://127.0.0.1:27017/")
dblist = myclient.list_database_names()
mydb = myclient["ResourcesDB"]
resDoubanBook = mydb["ResDoubanBook"]
resDoubanBook.create_index([("id",1)], unique=True)


session = requests.Session()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
}

class GetBook(object):

    async def fetch(self, url, data=''):
        try:
            myapp.info("%s 尝试请求" % data)
            conn=aiohttp.TCPConnector(verify_ssl=False) # 防止ssl报错
            async with aiohttp.ClientSession(connector=conn) as session:
                async with session.post(url,data=data) as resp:
                    myapp.info("%s 访问状态：%s" % (data, resp.status))
                    pageHtml = await resp.text()
                    await self.deal(data,pageHtml)
        except Exception as ex:
            myapp.error("%s -->请求失败：%s" % (data,ex))
    
    async def cip_control_sem(self,sem,url,data=''):
        async with sem:
            await self.fetch(url,data)

    async def deal(self, data, html):
        try:
            bsInPage = BeautifulSoup(html,'html.parser')
            cipData = bsInPage.find('pre').p.get_text()
            divInfo = bsInPage.find('div',{'id':'info'})
            # myapp.info(divInfo)
            comments = divInfo.find_all(text=lambda text: isinstance(text,Comment))
            comment1 = BeautifulSoup(comments[0],'html.parser')
            comment2 = BeautifulSoup(comments[1],'html.parser')
            author = comment1.find('td',text='第一责任者').next_sibling.next_sibling.get_text()
            pages = comment2.find('td',text='页数').next_sibling.next_sibling.get_text()
            printCount = comment2.find('td',text='印数（册）').next_sibling.next_sibling.get_text()
            cip = bsInPage.find('div',{'id':'info'}).find('td',text='CIP核准号').next_sibling.next_sibling.get_text()
            isbn = bsInPage.find('div',{'id':'info'}).find('td',text='ISBN').next_sibling.next_sibling.get_text()
            title = bsInPage.find('div',{'id':'info'}).find('td',text='正书名').next_sibling.next_sibling.get_text()
            series = bsInPage.find('div',{'id':'info'}).find('td',text='丛书名').next_sibling.next_sibling.get_text()
            publisher = bsInPage.find('div',{'id':'info'}).find('td',text='出版单位').next_sibling.next_sibling.get_text()
            pubplace = bsInPage.find('div',{'id':'info'}).find('td',text='出版地').next_sibling.next_sibling.get_text()
            pubdate = bsInPage.find('div',{'id':'info'}).find('td',text='出版时间').next_sibling.next_sibling.get_text()
            # author = bsInPage.find('div',{'id':'info'}).find('td',text='第一责任者').next_sibling.next_sibling.get_text()
            edition = bsInPage.find('div',{'id':'info'}).find('td',text='版次').next_sibling.next_sibling.get_text()
            printNum = bsInPage.find('div',{'id':'info'}).find('td',text='印次').next_sibling.next_sibling.get_text()
            price = bsInPage.find('div',{'id':'info'}).find('td',text='定价(元)').next_sibling.next_sibling.get_text()
            language = bsInPage.find('div',{'id':'info'}).find('td',text='正文语种').next_sibling.next_sibling.get_text()
            format = bsInPage.find('div',{'id':'info'}).find('td',text='开本或尺寸').next_sibling.next_sibling.get_text()
            binding = bsInPage.find('div',{'id':'info'}).find('td',text='装帧方式').next_sibling.next_sibling.get_text()
            # pages = bsInPage.find('div',{'id':'info'}).find('td',text='页数').next_sibling.next_sibling.get_text()
            # printCount = bsInPage.find('div',{'id':'info'}).find('td',text='印数（册）').next_sibling.next_sibling.get_text()
            catalogCode = bsInPage.find('div',{'id':'info'}).find('td',text='中图法分类').next_sibling.next_sibling.get_text()
            tags = bsInPage.find('div',{'id':'info'}).find('td',text='主题词').next_sibling.next_sibling.get_text()
            summary = bsInPage.find('div',{'id':'info'}).find('td',text='内容提要').next_sibling.next_sibling.get_text()
            bookinfo = {
                'cip':cip,
                'isbn':isbn,
                'title':title,
                'series':series,
                'publisher':publisher,
                'pubplace':pubplace,
                'pubdate':pubdate,
                'author':author,
                'edition':edition,
                'printNum':printNum,
                'Price':price,
                'language':language,
                'format':format,
                'binding':binding,
                'pages':pages,
                'printCount':printCount,
                'catalogCode':catalogCode,
                'tags':tags,
                'summary':summary
            }
            guid = str(uuid.uuid1()).replace("-","")
            mssql.ExecNonQuery("insert into ResCIPInfo (id,cip,isbn,title,author,series,publisher,pubplace,pubdate,edition,printNum,price,language,format,binding,catalogCode,tags,summary,cipData,pages,printCount) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (guid,cip,isbn,title,author,series,publisher,pubplace,pubdate,edition,printNum,price,language,format,binding,catalogCode,tags,summary,cipData,pages,printCount) )
            # myapp.info("cipData: %s" % cipData)
            myapp.info("bookinfo: %s" % bookinfo)
        except Exception as ex:
            myapp.error("%s解析失败：error为 %s" % (data,ex))

    def getDoubanBookById(self, id):
        baseUrl = "https://api.douban.com/v2/book/" + str(id) + "?apikey=0df993c66c0c636e29ecbb5344252a4a"
        response = session.get(baseUrl,headers=headers)
        resJson = json.loads(response.text)
        return resJson

    def getDoubanBookWithDB(self, id):
        try:
            myapp.info("id:{0}".format(id))
            resJson = self.getDoubanBookById(id)
            resCode = resJson.get("code")
            if resCode == None:
                # myapp.info(resJson)
                try:
                    resDoubanBook.insert(resJson)
                except Exception as err:
                    myapp.error("id:{0}数据库插入失败,错误信息：{1}".format(id,err))
        except Exception as err:
            myapp.error("id:{0}访问失败,错误信息：{1}".format(id,err))

    def getDoubanBook(self):
        id = resDoubanBook.find().sort([("id",-1)]).collation({'locale':'zh','numericOrdering':True}).limit(1)[0]['id']
        # id = resDoubanBook.find().sort('_id',-1).limit(1)[0]
        id = int(id) + 1
        myapp.info(id)
        lastId = id + 10000
        while id < lastId:
            self.getDoubanBookWithDB(id)
            id += 1
            time.sleep(2)

    def getCip(self):
        ssl._create_default_https_context = ssl._create_unverified_context
        url = "https://www.capub.cn:8443/pdm/business/CipInfoAction.do?method=checkApproveNo"
        lastCip = mssql.ExecQuery("select top 1 cip from rescipinfo order by cip desc")[0]['cip']
        myapp.info("最后的cip：{0}".format(lastCip))
        currentYear = datetime.now().year
        myapp.info("今年是{0}年".format(currentYear))
        sortCode = int(str(lastCip)) + 1
        if lastCip[0:4] != str(currentYear):
            sortCode = currentYear * 1000000
        lastCode = sortCode + 10000
        while sortCode < lastCode:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            sem = asyncio.Semaphore(300)
            tasks = []
            for code in range(sortCode,sortCode+100):
                sortCode = sortCode + 1
                task1 = asyncio.ensure_future(self.cip_control_sem(sem,url,{"approveNo":sortCode}))
                tasks.append(task1)
            loop.run_until_complete(asyncio.wait(tasks))

    
    def getbooks(self, startValue, pageSize):
        myapp.info("startValue:%d" % startValue)
        myapp.info("pageSize:%d" % pageSize)
        return resDoubanBook.find().limit(pageSize).skip(startValue)

    async def downImg(self, url):
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
                            imgPath = '../' + imgPath
                            print(imgPath)
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

    async def control_sem(self, sem, url):
        async with sem:
            await self.downImg(url)

    def DownCoverByData(self, data):
        # loop = asyncio.get_event_loop()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        sem = asyncio.Semaphore(300)
        tasks = []
        for rowData in data:  # 遍历图书信息
            objectId = rowData['_id']
            myapp.info("当前id为：%s" % objectId)
            images = rowData['images']
            task1 = asyncio.ensure_future(self.control_sem(sem,images['medium']))
            task2 = asyncio.ensure_future(self.control_sem(sem,images['large']))
            task3 = asyncio.ensure_future(self.control_sem(sem,images['small']))
            tasks.append(task1)
            tasks.append(task2)
            tasks.append(task3)
        loop.run_until_complete(asyncio.wait(tasks))
    
    def DownCover(self):
        row = 20421600
        count = resDoubanBook.count_documents({})
        ssl._create_default_https_context = ssl._create_unverified_context
        myapp.info("图书总量为：%d" % count)
        while row<count:
            myapp.info("当前批次为：%d" % row)
            try: 
                data = self.getbooks(row,100)
                self.DownCoverByData(data)
                row += 100
            except Exception as err:
                myapp.error("该批次处理失败：{0}".format(err))



if __name__=='__main__':
    getter = GetBook()
    getter.DownCover()