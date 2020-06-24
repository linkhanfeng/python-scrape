import urllib.request
import re

# 下载网页
def download(url, user_angent="wswp", retries_num = 2):
	print('下载网页::', url)
	try:
		req = urllib.request.Request(url)
		req.add_header('User-Agent', user_angent)
		html = urllib.request.urlopen(req).read().decode('utf-8')
	except urllib.request.URLError as e:
		print('下载网页 error::', e.reason)
		html = None
		if retries_num > 0:
			if hasattr(e, 'code') and 500 <= e.code < 600:
				print(' 500错误重试::', e.code, url)
				return download(url, retries_num - 1)
	return html

# 网站地图
def crawl_sitemap(url):
	sitemap = download(url)
	links = re.findall(r"<loc>(.*?)</loc>", sitemap)
	# print(links)
	for link in links:
		html = download(link)
		print('地图url::', link)

baidu = 'https://www.baidu.com/'
taobao = 'https://www.taobao.com/'
site_url = 'http://example.webscraping.com/'
sitemap_url = 'http://example.webscraping.com/sitemap.xml'
# html = download(taobao)
crawl_sitemap(sitemap_url)
# print(html)
