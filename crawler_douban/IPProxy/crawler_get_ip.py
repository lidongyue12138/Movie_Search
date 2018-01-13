# coding=utf-8

import urllib2
import json
import requests
from bs4 import BeautifulSoup
from random import choice
import os

def test_if_can_get_ip():
    url = "http://localhost:8000/?country=国内&protocol=0"
    content = urllib2.urlopen(url).read()
    return content

def print_ip_address(content):
    try:
        content = json.loads(content)
        print(type(content[0]))
        for i in content:
            print(i)
            #print("%s\t%s\t%s" %(ip_ad.split(",")))
    except Exception as e:
        print(e)

def get_ip():
    url = "http://localhost:8000/?country=国内"
    content = urllib2.urlopen(url).read()
    content = json.loads(content)
    for ip in content:
        ad, port, score = ip
        ad.encode("utf-8")
        ip_addr = "%s:%s" %(ad, str(port))
        yield ip_addr

def check_ip_address():
    proxys = []
    for ip in get_ip():
        proxy_temp = {"http":"http://%s" %ip, "https": "http://%s" %ip}
        proxys.append(proxy_temp)
    print(proxys[0])
    url = "http://movie.douban.com/"
    for proxy in proxys:
        try:
            proxy=urllib2.ProxyHandler(proxy)
            opener=urllib2.build_opener(proxy)
            #urllib2.install_opener(opener)
            res = opener.open(url, timeout=5).read()
            print res
        except Exception,e:
            print proxy
            print e
            continue

def check_if_not_sjtu(ip):
    proxy_temp = {"http": "http://%s" %(ip)}

    url = "http://ip.chinaz.com/getip.aspx"
    try:
        proxy=urllib2.ProxyHandler(proxy_temp)
        opener=urllib2.build_opener(proxy)
        #urllib2.install_opener(opener)
        res = opener.open(url, timeout=5).read()
        print("checking sjtu ip address")
        if "上海交通大学" in res:
            return False
        else:
            return True
    except Exception,e:
        print proxy
        print e
        return False

def save_ip(ip):
    print(ip)
    index_filename = 'ip.txt'
    f = open(index_filename, 'a')
    f.write(ip+'\n')
    f.close()

def valid_name(s):
    import string
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    s = ''.join(c for c in s if c in valid_chars)
    return s

if __name__ == '__main__':
    url = "https://movie.douban.com/subject/1292052/"

    # for ip in get_ip():
    #     # if check_if_not_sjtu(ip):
    #     try:
    #         proxies = {"http": "http://%s" % (ip), "https": "http://%s" % (ip)}
    #         #proxies = {"https": "http://%s" % (ip)}
    #         headers = { "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "Accept-Encoding":"gzip, deflate", "Accept-Language":"zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3", "Connection":"keep-alive", "Content-Length":"31", "Content-Type":"application/x-www-form-urlencoded", "User-Agent":"Mozilla/5.0 (Windows NT 5.1; rv:11.0) Gecko/20100101 Firefox/11.0" }
    #         proxy=urllib2.ProxyHandler(proxies)
    #         opener=urllib2.build_opener(proxy)
    #         #urllib2.install_opener(opener)
    #         res = opener.open(url, timeout=5).read()
    #         if len(res)>500:
    #             save_ip(ip)
    #             print("success!")
    #             #print(res.text)
    #         #print(BeautifulSoup(res.text))
    #     except Exception as e:
    #         print(e)
    #     # else:
    #     #     continue
    #     # print(check_if_not_sjtu(ip))
    folder = "html"
    content = urllib2.urlopen(url).read()
    filename = valid_name(url)
    if os.path.exists(os.path.join(folder, filename)):
        print("exist!")
    else:
        print("saving!")
        f = open(os.path.join(folder, filename), 'w')
        f.write(content)  # 将网页存入文件
        f.close()
