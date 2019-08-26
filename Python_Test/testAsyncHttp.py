import asyncio
import time
import pymssql
from urllib.request import urlopen,Request
from urllib.error import HTTPError
from bs4 import BeautifulSoup
from urllib import request
import aiohttp
import lxml

# 连接数据库
conn = pymssql.connect(server='127.0.0.1',user='sa',password='123456',database='ResourcesDB')
cur = conn.cursor()
if not cur:
    raise NameError("数据库连接失败")

async def testInsertToDb(url):
    inPageHtml = request.urlopen(url)
    bsInPage = BeautifulSoup(inPageHtml,'lxml')
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
    cur.execute("insert into ResBookInfoTest2 (PageUrl,Title,Isbn,ImgUrl,Marc,CreateTime) values (%s,%s,%s,%s,%s,%s)",(url,bookTitle,bookIsbn,bookCover,bookMarc,timeStr))
    conn.commit()

async def dealPage(response):
    print(response.text)
    bsInPage = BeautifulSoup(response.text(),'lxml')
    bookTitle = bsInPage.find('table',{'id':'bookInfoTable'}).h2.get_text()
    bookIsbn = bsInPage.find('img',{'id':'bookcover_img'}).get('isbn')
    bookMarc = bsInPage.find('div',{'id':'bookMarcDiv'}).pre.get_text().replace('\u0000', '').replace('\x00', '')
    bookCover = None
    url = None
    timeStr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    cur.execute("insert into ResBookInfoTest2 (PageUrl,Title,Isbn,ImgUrl,Marc,CreateTime) values (%s,%s,%s,%s,%s,%s)",(url,bookTitle,bookIsbn,bookCover,bookMarc,timeStr))
    conn.commit()

async def testAsyncHttp(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            print(response.status)
            print(response.text())
            print(response.text)
            # return await dealPage(response)

def main():
    tasks = None
    print(f"started at {time.strftime('%X')}")
    tasks = [asyncio.ensure_future(testAsyncHttp('http://opac.gzlib.gov.cn/opac/book/3002004477')) for mill in range(1,10)]
    print(f"prepared at {time.strftime('%X')}")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(tasks))
    print(f"finished at {time.strftime('%X')}")

main()
while 1:
    pass