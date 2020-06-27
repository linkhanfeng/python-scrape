from array import array
from urllib.parse import urlparse
from urllib.parse import urljoin
import urllib.robotparser
import re

biliPaging = 'https://www.bilibili.com/v/anime/information/#/all/default/0/{0}/'
url = biliPaging.format('2333')
print(url)
arr = [{'a':1}, {'a':2}]
print(arr[1]['a'])

count = 2
count -= 1
print(count)

# url1 = 'http://example.webscraping.com/places/default/view/Afghanistan-1'
baseUrl = 'http://example.webscraping.com/'
url1 = '/places/default/view/Afghanistan-1'
url2 = '/places/default/iso/CN'
purl = urlparse(url1)
# if purl.path == '' and purl.query == '':
#     print('退出')
# else:
#     purl.scheme = baseUrl.scheme
# else if purl.scheme == '':
#     purl.scheme = baseUrl.scheme
urlJoined = urljoin(baseUrl, url1)
print(purl, baseUrl)
print(2333, urlJoined)

lista = [1, 2, 3, 4]
print(55555, 2 in lista)
print( len(lista) )

reg1 = '/places/default/(view|iso)'
print(re.match(reg1, url1))

ccc11 = re.findall('Country: </label></td><td class="w2p_fw">(.*?)</td>', 'Country: </label></td><td class="w2p_fw">china</td>')
print(ccc11[0])

def robotTxt(rebotUrl=None, userAngent=None, url="/"):
    rp = urllib.robotparser.RobotFileParser()
    can_fetch = True
    try:
        rp.set_url(rebotUrl)
        rp.read()
        can_fetch = rp.can_fetch(userAngent, url)
    except Exception as e:
        print('未找到 robots.txt 文件::')
    print(233333, rp.site_maps())
    return {
        'can_fetch': can_fetch,
        # 'site_maps': rp.site_maps()
    }

# cd1 = robotTxt('http://example.webscraping.com/robots.txt', "*", 'http://example.webscraping.com/places/default/view/Afghanistan-1')
# print(cd1)
cd2 = robotTxt(rebotUrl='http://example.webscraping.com/robots.txt', userAngent="*")
print(cd2)
