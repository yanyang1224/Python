import pymongo
import requests
import json
import logging
import logging.handlers
import time
from urllib.request import urlopen,Request
from urllib.error import HTTPError
from urllib import request
from Util.LogHandler import LogHandler


mylog = LogHandler('test')

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
dblist = myclient.list_database_names()
mydb = myclient["ResourcesDB"]
resDoubanBook = mydb["ResDoubanBook"]
resDoubanBook.create_index([("id",1)], unique=True)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
}
userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
proxies = None
session = requests.Session()

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


def getProxyFromWanDou():
    try:
        proxy_support = request.ProxyHandler(proxies=None)
        opener = request.build_opener(proxy_support)
        opener.addheaders = [('User-agent', userAgent)]
        request.install_opener(opener)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'}
        requestProxy = Request('http://api.wandoudl.com/api/ip?app_key=1e17571a889de3574c02467b4d8c1cd8&pack=0&num=1&xy=1&type=1&lb=\r\n&mr=1&',headers=headers)
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

def getbookbyid(id):
    baseUrl = "https://api.douban.com/v2/book/" + str(id) + "?apikey=0df993c66c0c636e29ecbb5344252a4a"
    response = session.get(baseUrl,headers=headers)
    resJson = json.loads(response.text)
    return resJson

def getbookbysearch(q,start=0,count=100):
    baseUrl = "https://api.douban.com/v2/book/search?apikey=0df993c66c0c636e29ecbb5344252a4a&q=" + str(q) +"&start=" + str(start) + "&count=" + str(count)
    response = session.get(baseUrl,headers=headers)
    resJson = json.loads(response.text)
    return resJson

def getbookbyseriesid(id,start=0,count=100):
    baseUrl = "https://api.douban.com/v2/book/series/" + str(id) + "/books?apikey=0df993c66c0c636e29ecbb5344252a4a&count=" + str(count) + "&start=" + str(start)
    response = session.get(baseUrl,headers=headers)
    resJson = json.loads(response.text)
    return resJson
    # return resJson.get("books") if resJson.get("books") != '' else None

def rungetbookbysearch():
    searchWords = [chr(i) for i in range(ord("a"),ord("z")+1)]
    for searchWord in searchWords:
        try:
            myapp.info("searchWord:{0}".format(searchWord))
            resJson = getbookbysearch(searchWord)
            resTotal = resJson.get("total")
            resCount = resJson.get("count")
            resBooks = resJson.get("books")
            resCode = resJson.get("code")
            # myapp.info(resCode == None)
            myapp.info(len(resBooks))
            myapp.info(len(resBooks)>0)
            myapp.info("count:{0}".format(resCount))
            if resCode == None:
                resDoubanBook.insert_many(resBooks)
                if resTotal > resCount:
                    synclen = resCount
                    while resTotal > synclen:
                        myapp.info("searchWord:{0},synclen:{1}".format(searchWord,synclen))
                        resJson = getbookbysearch(searchWord,synclen)
                        resBooks = resJson.get("books")
                        resCode = resJson.get("code")
                        # resCount = resJson.get("count")
                        if resBooks != None and len(resBooks) > 0:
                            resDoubanBook.insert_many(resBooks)
                        else:
                            myapp.error("searchWord:{0},synclen:{1}系列访问失败，失败代码：{2}".format(searchWord,synclen,resCode))
                        synclen += resCount
                        time.sleep(2)
            else:
                myapp.error("searchWord:{0}系列访问失败，失败代码：{1}".format(searchWord,resCode))
            time.sleep(2)
        except Exception as err:
            myapp.error("该系列访问失败：{0}".format(err))
            time.sleep(2)
        
def rungetbookbyid(id):
    try:
        myapp.info("id:{0}".format(id))
        resJson = getbookbyid(id)
        resCode = resJson.get("code")
        if resCode == None:
            # myapp.info(resJson)
            try:
                resDoubanBook.insert(resJson)
            except Exception as err:
                myapp.error("id:{0}数据库插入失败,错误信息：{1}".format(id,err))
    except Exception as err:
        myapp.error("id:{0}访问失败,错误信息：{1}".format(id,err))

def run():
    seriesId = 1
    count = 49173
    while seriesId < count:
        try:
            myapp.info(seriesId)
            resJson = getbookbyseriesid(seriesId)
            resTotal = resJson.get("total")
            resCount = resJson.get("count")
            # resStart = resJson.get("start")
            resBooks = resJson.get("books")
            resCode = resJson.get("code")
            # myapp.info(resCode)
            # myapp.info(resTotal)
            # myapp.info(resCount)
            # myapp.info(resStart)
            # myapp.info(resBooks)
            if resCode == None:
                resDoubanBook.insert_many(resBooks)
            else:
                myapp.error("id:{0}系列访问失败，失败代码：{1}".format(seriesId,resCode))
            
            if resTotal>resCount:
                synclen = resCount
                while resTotal>synclen:
                    resJson = getbookbyseriesid(seriesId,synclen)
                    # resTotal = resJson.get("total")
                    # resCount = resJson.get("count")
                    # resStart = resJson.get("start")
                    resBooks = resJson.get("books")
                    resCode = resJson.get("code")
                    if resCode==None:
                        resDoubanBook.insert_many(resBooks)
                    else:
                        myapp.error("id:{0}系列访问失败，失败代码：{1}".format(seriesId,resCode))
                    synclen += resCount
                
        except Exception as err:
            myapp.error("该系列访问失败：{0}".format(err))
        seriesId += 1
        time.sleep(2)

if __name__=="__main__":
    # run()
    # rungetbookbysearch()
    id = 1002046
    while True:
        rungetbookbyid(id)
        id += 1
        time.sleep(2)