import socks
import socket
import time
import urllib
from urllib.request import urlopen,Request
from stem import Signal
from stem.control import Controller


# 让Tor重建连接，获得新的线路
def renew_connection():
    with Controller.from_port(port = 9151) as controller:
        controller.authenticate()
        controller.signal(Signal.NEWNYM)
        controller.close()

# socks.set_default_proxy(socks.SOCKS5,"localhost",9150)
# socket.socket = socks.socksocket
while 1:
    request = Request('http://icanhazip.com')
    request.set_proxy('127.0.0.1:9150','SOCKS5')
    print(urlopen(request).read())
    renew_connection()
    # print(urlopen('https://www.baidu.com').read())
    # print(urlopen('http://opac.zjlib.cn/opac/search?q=*%3A*&searchType=standard&isFacet=false&view=simple&searchWay=class&rows=10&sortWay=score&sortOrder=desc&searchWay0=marc&logical0=AND&page=1').read())
    time.sleep(5)