from urllib.request import urlopen
from bs4 import BeautifulSoup
from urllib.error import HTTPError

# try:
#     html = urlopen('http://www.baidu.com')
# except HTTPError as e:
#     print(e)
# else:
#     bs = BeautifulSoup(html.read(),'html.parser')
#     print(bs.p)
html = urlopen('http://www.pythonscraping.com/pages/page1.html')
bs = BeautifulSoup(html.read(),'html.parser')
nameList = bs.findAll('span',{'classs':'green'})
for name in nameList:
    print(name.get_text())