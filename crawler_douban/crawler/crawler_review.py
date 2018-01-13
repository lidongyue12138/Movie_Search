# coding=utf-8
import urllib2, cookielib, urllib
from threading import Thread, Lock, stack_size
from Queue import Queue
import os
import time
import re
import urlparse
from collections import namedtuple
from bs4 import BeautifulSoup
import socket
from gzip import GzipFile
from StringIO import StringIO
import zlib
from random import randint, choice
from collections import defaultdict
import requests

from configure import USER_AGENTS, ip_addrs

from multiprocessing import Queue, Process

def get_review_href(q):
    f = open("review.txt", "r")
    for review in f.readlines():
        try:
            q.put(review)
        except:
            print("get review href FAIL!!!!")
            pass

socket.setdefaulttimeout(10)


class Fetcher_review:
    #拿到review的url，返回review的html
    def __init__(self, receiving_queue, sending_queue, review_set):
        self.receiving_queue = receiving_queue
        self.sending_queue = sending_queue
        self.review_set = review_set

        self.time = time.time()
        while(True):
            if (time.time()-self.time < 0.5):
                continue
            self.time = time.time()
            try:
                page = self.receiving_queue.get()
            except:
                continue
            id_num = self.getFilenameID(page)
            if not self.check_repeating(id_num):
                continue

            content = self._to_crawl_review(page)
            #print(content)
            self._add_page_to_folder(content, page)

    #不停更换ip，和浏览器头部
    def _to_crawl_review(self, page):
        try:
            # ip = choice(ip_addrs)
            # proxies = {"http": "http://%s" % (ip), "https": "http://%s" % (ip)}
            headers = {"User-Agent": choice(USER_AGENTS)}
            # proxy = urllib2.ProxyHandler(proxies)
            # opener = urllib2.build_opener(proxy)
            # urllib2.install_opener(opener)
            req = urllib2.Request(url=page, headers=headers)
            content = urllib2.urlopen(req).read()
            time.sleep(1)
            return content
        except socket._GLOBAL_DEFAULT_TIMEOUT:
            print("timeout")
            return None
        except urllib2.URLError:
            # print(ip)
            print("url error: " + page)
            #ip_addrs.remove(ip)
            return None
        except Exception as e:
            print (e)
            return None

    def _valid_filename(self, s):
        import string
        valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        s = ''.join(c for c in s if c in valid_chars)
        return s

    def check_repeating(self, id_num):
        id_num = id_num.strip()
        if id_num in self.review_set:
            return False
        return True

    def save_to_set(self, id_num):
        id_num = id_num.strip()
        self.review_set.add(id_num)
        save_review = open("crawler/save_review.txt", "a")
        save_review.write(id_num+"\n")
        save_review.close()

    def getFilenameID(self, filename):
        id_num = [i for i in filename if "0"<=i<="9"]
        id_num = "".join(id_num)
        return id_num

    def _add_page_to_folder(self, content, page):
        if content == None:
            return
        folder = 'reviews'  # 存放网页的文件夹
        filename = self._valid_filename(page)  # 将网址变成合法的文件名

        id_num = self.getFilenameID(page)
        if not os.path.exists(folder):  # 如果文件夹不存在则新建
            os.mkdir(folder)
        print("saving one review: "+ filename)
        f = open(os.path.join(folder, filename), 'w')
        f.write(content)  # 将网页存入文件
        f.close()
        self.sending_queue.put((id_num, os.path.join("reviews", filename)))


if __name__ == '__main__':
    review_set = set()
    save_review = open("crawler/save_review.txt", "r")
    for line in save_review.readlines():
        line = line.strip()
        review_set.add(line)
    save_review.close()

    # q = Queue()
    # writer = Process(target=get_review_href, args=(q,))
    # writer.start()
    #
    # reader = Process(target=Fetcher_review, args=(q, review_set))
    # reader.start()
    #
    # reader.join()
    # writer.join()
