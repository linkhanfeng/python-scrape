import builtwith
import whois

webBuiltwith = builtwith.parse('http://example.webscraping.com/')
print('webBuiltwith::', webBuiltwith)

webWhois = whois.whois('https://www.baidu.com/')
print('webWhois::', webWhois)

