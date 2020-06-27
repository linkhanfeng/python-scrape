import urllib.request
import re
import itertools
import urllib.robotparser
from urllib.parse import urlparse
from urllib.parse import urljoin
import logging

import builtwith
import whois

logging.basicConfig(filename='log/log.log',level=logging.INFO) # DEBUG

class Spider:
    name = '爬虫类'

    def __init__(self, url, userAngent='Googlebot', checkRobot=True):
        self.url = url
        self.userAngent = userAngent
        self.checkRobot = checkRobot
        self.location = urlparse(url)
        self.urlInfo = self.getUrlInfo()

    def getUrlInfo(self):
        baseUrl = '{0}://{1}/'.format(self.location.scheme, self.location.hostname)
        urlInfo = {
            'root': baseUrl,
            'robots': '{0}robots.txt'.format(baseUrl),
            'sitemap': '{0}sitemap.xml'.format(baseUrl),
        }
        return urlInfo
    # ------------------------------------------------------------------------
    # 1.1 爬虫作用: 收集数据,效率
    # 1.2 爬虫合法性: 请记住自己是该网站的访客,应当约束自己的行为;
    # ------------------------------------------------------------------------
    # 1.3.1 检查 (robots.txt)
    def robotTxt(self, rebotUrl=None, userAngent=None, url="/"):
        '''[summary]

        检测 robots.txt 协议

        Keyword Arguments:
            rebotUrl {str} -- robots.txt地址 (default: {None})
            userAngent {str} -- ua (default: {None})
            url {str} -- 检测此url是否被允许抓取 (default: {"/"})

        Returns:
            [dict] -- can_fetch: 是否可以抓取网页, site_maps: 网站地图 crawl_delay: 抓取间隔
        '''
        rebotUrl= rebotUrl if rebotUrl else self.urlInfo['robots']
        userAngent= userAngent if userAngent else self.userAngent
        rp = urllib.robotparser.RobotFileParser()
        can_fetch = True
        try:
            rp.set_url(rebotUrl)
            rp.read()
            can_fetch = rp.can_fetch(userAngent, url)
        except Exception as e:
            print('未找到 robots.txt 文件::')

        return {
            'can_fetch': can_fetch,
            'site_maps': rp.site_maps(),
            'crawl_delay': rp.crawl_delay(userAngent),
        }

    # 1.3.2 检查网站地图 (sitemap.xml)
    # ------------------------------------------------------------------------
    # 1.3.3 估算网站页面数量 使用百度等搜索引擎估算
    def siteSize(self, searchEngine='baidu'):
        if searchEngine == 'baidu':
            url = 'http://www.baidu.com/s?wd=site:({0})'.format(self.location.hostname)
        html = self.download(url)
        try:
            pages = re.findall(r'找到相关结果数约(.*?)个', html)[0].replace(',', '')
            pages = int(pages)
        except Exception as e:
            pages = 0
        return pages

    # ------------------------------------------------------------------------
    # 1.3.4 识别网站采用的技术 框架
    def siteFrame(self):
        webBuiltwith = builtwith.parse(self.url)  # builtwith 模块无法识别 UGC 类型的网站;
        return webBuiltwith

    # ------------------------------------------------------------------------
    # 1.3.5 识别网站所有者 等信息
    def siteWhois(self):
        webWhois = whois.whois(self.location.hostname)
        return webWhois

    # ------------------------------------------------------------------------
    # 1.4 编写网络爬虫
    # 1.4.1 下载网页
    def download(self, url=None, userAngent=None, retriesNum=2, fixUrl=True):
        '''[summary]

        下载网页

        Keyword Arguments:
            url {str} -- 网址 (default: {None})
            userAngent {str} -- 浏览器标识 (default: {'Googlebot'})
            retriesNum {number} -- 遇到服务器5XX错误重试次数 (default: {2})
            fixUrl {bool} -- url解析错误时尝试修复 (default: {True})

        Returns:
            [str] -- [网页字符串]
        '''
        url = url if url else self.url
        userAngent = url if url else self.userAngent
        # html = None
        html = ''
        try:
            req = urllib.request.Request(url)
            req.add_header('User-Agent', userAngent)
            html = urllib.request.urlopen(req).read().decode('utf-8')
            print('下载网页OK::', url)
        except urllib.request.HTTPError as e:
            print('服务器返回错误::', e.reason)
            if retriesNum > 0:
                if hasattr(e, 'code') and 500 <= e.code < 600:
                    print(' 500错误重试::', e.code, url)
                    return self.download(url, retriesNum - 1)
        except ValueError as e:
            if fixUrl:
                tryUrl = urljoin(self.urlInfo['root'], url)
                return self.download(tryUrl, fixUrl=False)
            else:
                print('url格式错误,原始地址在上一条log::', url)
        return html

    # ------------------------------------------------------------------------
    # 1.4.2 获取网站地图链接 sitemap.xml (仅供参考)
    def sitemapUrls(self):
        sitemapPage = self.download(self.urlInfo['sitemap'])
        links = re.findall(r"<loc>(.*?)</loc>", sitemapPage)
        # TODO::遇到 xml 递归
        # for link in links:
        #     html = download(link)
        return links

    # ------------------------------------------------------------------------
    # 1.4.3 抓取有规律的分页数据 通过页面 id 遍历
    def crawlPaginationById(self, pageUrl=None, count=3, maxErrors=5):
        '''[summary]

        该方法只能抓取数据库 自增ID 的分页数据,类似亚马逊isbn号作为分页的页面无法使用方法抓取

        Keyword


        Arguments:
            pageUrl {str} -- 分页链接
            count {number} -- 最大抓取页面限制, 传入 -1 无限制 (default: {3})
            maxErrors {number} -- 允许的最大错误数 (default: {5})

        Returns:
            array -- 抓取的分页数据
        '''
        pageUrl = pageUrl if pageUrl else self.url
        errorsNum = 0
        pages = []
        for pageNum in itertools.count(1):
            if count == 0:
                break
            url = pageUrl.format(pageNum)
            html = self.download(url)
            if not html:
                errorsNum += 1
            if errorsNum == maxErrors:
                break
            else:
                pages.append({
                    'id': pageNum,
                    'title': re.findall(r'<title(.*?)>(.*?)</title>', html),
                    # 'html': html
                })
            count -= 1
        return pages

    # ------------------------------------------------------------------------
    # 1.4.4 链接爬虫
    def crawlLinksFromPage(self, seedUrl=None, linkReg='^[http|https]'):
        '''[summary]

        爬取网页中的所有特定类型的链接

        Keyword Arguments:
            seedUrl {str} -- 指定网页地址 (default: {None})
            linkReg {str} -- 在种子网页中筛选出需要的链接地址的正则表达式 (default: {'^[http|https]'})

        Returns:
            list -- 筛选出的所有符合条件的链接地址
        '''
        seedUrl = seedUrl if seedUrl else self.url
        linkDatas = [] # 存储爬取的数据
        seen = [seedUrl] # 防止重复下载链接
        crawlQueue = [seedUrl] # 爬取队列
        num = 0
        while crawlQueue:
            num += 1
            if (num % 10 == 0):
                print('发现目标数量/已爬取数量::', len(seen), len(linkDatas))
            url = crawlQueue.pop()
            html = ''

            if self.robotTxt(url=url)['can_fetch']:
                html = self.download(url)
                # 测试数据处理
                linkDatas.append({
                    'url': url,
                    'size': len(html),
                    'country': re.findall('Country: </label></td><td class="w2p_fw">(.*?)</td>', html),
                    'flag': re.findall('<img[^>]+src=["\'](.*?)["\']', html),
                })
            else:
                print('协议禁止抓取::', url)
                linkDatas.append({ 'url': url, 'robots': 'Disallow' })

            for link in self.getLinks(html):
                if re.match(linkReg, link) and (link not in seen):
                    seen.append(link)
                    crawlQueue.append(link)

        logging.info(linkDatas)
        return linkDatas

    def getLinks(self, html):
        '''[summary]

        获取一个网页中的所有 a标签

        Arguments:
            html {str} -- [网页字符串]

        Returns:
            [array] -- [网页中的所有链接]
        '''
        # 正则分心 <a 开头    [^>]+ 匹配任意非`>`字符    href=["\'](.*?)["\'] 匹配href链接
        hrefReg = re.compile('<a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)
        links = hrefReg.findall(html)
        return links


baiduUrl = 'http://www.baidu.com/'
bilibiliUrl = 'https://www.bilibili.com/'
biliPaging = 'https://www.bilibili.com/v/anime/information/#/all/default/0/{0}/'  # 番剧资讯分页
exampleUrl = 'http://example.webscraping.com/'

spider = Spider(exampleUrl)
# print('urlInfo::', spider.location, spider.urlInfo)
# logging.info(spider.download('http://example.webscraping.com/places/default/iso/CN'))
# print('robotTxt::', spider.robotTxt())
# print('siteSize::', spider.siteSize())
# print('siteFrame::', spider.siteFrame())
# print('siteWhois::', spider.siteWhois())
# print('sitemapUrls::', spider.sitemapUrls())
# print('crawlPaginationById::', spider.crawlPaginationById(biliPaging))
print('crawlLinksFromPage::', spider.crawlLinksFromPage('/places/default/iso/CN', '/places/default/iso'))

# spider2 = Spider(exampleUrl, userAngent='BadCrawler')
# print('crawlLinksFromPage02::', spider2.crawlLinksFromPage(exampleUrl, '/places/default/(view|iso)'))

print('python ok!!!')
