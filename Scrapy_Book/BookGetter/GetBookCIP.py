from Util.LogHandler import LogHandler
from Util.MSSQLHelper import MSSQLHelper
import aiohttp
import asyncio
import ssl
import json
import datetime
import uuid
from bs4 import BeautifulSoup,Comment

mylog = LogHandler('test')
mssql = MSSQLHelper('127.0.0.1','sa','123456','ResourcesDB')

class GetBookCIP(object):

    async def fetch(self, url, data=''):
        try:
            mylog.info("%s 尝试请求" % data)
            conn=aiohttp.TCPConnector(verify_ssl=False) # 防止ssl报错
            async with aiohttp.ClientSession(connector=conn) as session:
                async with session.post(url,data=data) as resp:
                    mylog.info("%s 访问状态：%s" % (data, resp.status))
                    pageHtml = await resp.text()
                    await self.deal(data,pageHtml)
        except Exception as ex:
            mylog.error("%s -->请求失败：%s" % (data,ex))
    
    async def control_sem(self,sem,url,data=''):
        async with sem:
            await self.fetch(url,data)

    async def deal(self, data, html):
        try:
            bsInPage = BeautifulSoup(html,'html.parser')
            cipData = bsInPage.find('pre').p.get_text()
            divInfo = bsInPage.find('div',{'id':'info'})
            # mylog.info(divInfo)
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
            mssql.ExecNonQuery("insert into ResCIPInfo values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (guid,cip,isbn,title,author,series,publisher,pubplace,pubdate,edition,printNum,price,language,format,binding,catalogCode,tags,summary,cipData,pages,printCount) )
            # mylog.info("cipData: %s" % cipData)
            mylog.info("bookinfo: %s" % bookinfo)
        except Exception as ex:
            mylog.error("%s解析失败：error为 %s" % (data,ex))


    def run(self):
        ssl._create_default_https_context = ssl._create_unverified_context
        url = "https://www.capub.cn:8443/pdm/business/CipInfoAction.do?method=checkApproveNo"
        for year in range(2003,2021):
            sortCode = 0
            while sortCode < 300000:
                loop = asyncio.get_event_loop()
                sem = asyncio.Semaphore(300)
                tasks = []
                for code in range(sortCode,sortCode+100):
                    approveNo = year * 1000000 + code
                    task1 = asyncio.ensure_future(self.control_sem(sem,url,{"approveNo":approveNo}))
                    tasks.append(task1)
                sortCode += 100
                loop.run_until_complete(asyncio.wait(tasks))

if __name__=='__main__':
    getbook = GetBookCIP()
    getbook.run()