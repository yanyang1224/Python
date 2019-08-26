import requests  
from lxml import html  
import sys  
import urlparse
import collections
import time
from PIL import Image
import os
import random
 
import stem
import stem.connection
 
from stem import Signal
from stem.control import Controller
 
 
URL = "http://meizitu.com" # 要爬取的网站
 
# 根据图片大小过滤，单位像素
WIDTH = 500
HEIGHT = 500
 
# 抓取url队列
url_queue = collections.deque()
url_queue.append(URL)
 
# 抓取过的url
url_crawled = set()
url_crawled.add(URL)
 
# 抓取过的图片url
url_image = set()
 
# 代理
proxies = {
  'http': '127.0.0.1:1080'
}
 
# 让Tor重建连接，获得新的线路
def renew_connection():
    with Controller.from_port(port = 1051) as controller:
        controller.authenticate()
        controller.signal(Signal.NEWNYM)
        controller.close()
 
def get_public_ip(headers):
    res = requests.get("http://icanhazip.com", headers = headers, proxies = proxies)
    print(res.content)
    
 
# 单线程抓取
while(len(url_queue)):
    renew_connection()  # 每次循环都会更换IP

    print("Url queue length is %d",(len(url_queue))
    
    url = url_queue.popleft()
 
	headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
 
        get_public_ip(headers)
 
	response = requests.get(url, headers = headers, proxies = proxies)
	content_body = html.fromstring(response.content)
 
	parsed_body = html.fromstring(response.text)
	images = parsed_body.xpath('//img/@src')
 
	images = {urlparse.urljoin(response.url, url) for url in images}
	print("Found %d image in %s",(len(images), url))
 
	# 下载图片
	for image in images - url_image:
		r = requests.get(image, headers = headers, proxies = proxies)
 
		filename = image.split('/')[-1]
		now = time.localtime(time.time())
		year, month, day, hour, minute, second, weekday, yearday, daylight = now
		
		file_path = "girl_images/" + "%02d:%02d:%02d-" % (year, month, day) + "%02d:%02d:%02d-" % (hour, minute, second) + filename
 
		f = open(file_path, 'w')
		f.write(r.content)
		f.close()
		
		try:
			img = Image.open(file_path)
			width = img.size[0]
			height = img.size[1]
			if width <= WIDTH or height <= HEIGHT:
				os.remove(file_path)
			else:
				print file_path
 
			url_image.add(image)
 
			time.sleep(random.randint(1,3))
		except IOError:
			print "pillow can not open image"
 
 
	# 获取网页上所有url
	links = {urlparse.urljoin(response.url, url) for url in content_body.xpath('//a/@href') if urlparse.urljoin(response.url, url).startswith('http')}
	
	for link in links - url_crawled:
		if link.startswith('http://www.meizitu.com') is True or link.startswith('http://meizitu.com') is True:   # 限制爬取范围，不去别的网站
			url_crawled.add(link)
			url_queue.append(link)
 
	time.sleep(random.randint(1,5))