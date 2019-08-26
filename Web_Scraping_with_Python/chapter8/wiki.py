from urllib.request import urlopen,Request
from bs4 import BeautifulSoup

def getNgrames(content,n):
    content = content.split(' ')
    output = []
    for i in range(len(content) - n + 1):
        output.append(content[i:i+n])
    return output

headers = {'User-Agent': 'User-Agent:Mozilla/5.0'}
request = Request('http://en.wikipedia.org/wiki/Python_(programming_language)',headers=headers)
html = urlopen(request)
bs = BeautifulSoup(html,'html.parser')
content = bs.find('div',{'id':'mw-content-text'}).get_text()
ngrams = getNgrames(content,2)
print(ngrams)
print('2-grams count is: ' + str(len(ngrams)))
