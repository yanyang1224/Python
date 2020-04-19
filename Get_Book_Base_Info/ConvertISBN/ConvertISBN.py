from Util.LogHandler import LogHandler
from Util.MSSQLHelper import MSSQLHelper
import aiohttp
import asyncio
import ssl
import json
import datetime
import uuid
from bs4 import BeautifulSoup,Comment
from Util.isbn import Isbn

mylog = LogHandler('test')
mssql = MSSQLHelper('127.0.0.1','sa','123456','ResourcesDB')

class ConvertISBN(object):

    def run(self):
        # isbn= Isbn('978-7-5610-6751-2')
        # mylog.info(isbn.isbn10)
        count = mssql.ExecQuery("select top 1 cip from rescipinfo order by cip desc")[0]["cip"]
        mylog.info(count)
        cip = '0'
        while cip < count:
            resultList = mssql.ExecQuery("select top 1000 cip,isbn from rescipinfo where cip>%s and (isbn10 is null or isbn 13 is null) order by cip",(cip,))
            try:
                # mylog.info(resultList)
                for item in resultList:
                    try:
                        mylog.info(item)
                        isbn = Isbn(item["isbn"])
                        cip = item["cip"]
                        isbn10 = isbn.isbn10
                        isbn13 = isbn.isbn13
                        mssql.ExecNonQuery("update rescipinfo set isbn10=%s,isbn13=%s where cip=%s",(isbn10,isbn13,cip))
                    except Exception as ex:
                        mylog.error(ex)
            except Exception as ex:
                mylog.error(ex)

if __name__=='__main__':
    convert = ConvertISBN()
    convert.run()