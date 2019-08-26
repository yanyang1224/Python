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


def getProxy():
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'}
        requestProxy = Request('http://localhost:5010/get/',headers=headers)
        proxyResponse = urlopen(requestProxy)
        return proxyResponse.read().decode(encoding="utf8")
    except HTTPError as httperror:
        print("获取代理请求失败：{0}".format(httperror))
        time.sleep(5)
        getProxy()
    except Exception as err:
        print("获取代理失败：{0}".format(err))
        return None

while 1:
    print(getProxy())