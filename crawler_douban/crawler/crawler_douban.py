# coding=utf-8
import urllib2, cookielib, urllib
from threading import Thread, Lock, stack_size
import Queue as q
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
import random

from configure import USER_AGENTS, ip_addrs
from multiprocessing import Queue, Process

root_name = "https://movie.douban.com/subject/"



class Fetcher_movie:
    def __init__(self, thread_num, movie_set, sending_queue, urls = []):
        self.sending_queue = sending_queue
        self.to_crawlq = q.Queue()
        for url in urls:
            self.to_crawlq.put(url)


        #去重集合
        self.movie_set = movie_set
        try:
            for i in random.sample(list(self.movie_set), 20):
                self.to_crawlq.put(os.path.join(root_name, i))
        except:
            pass
        self.time = time.time()

        # self.stop = stop
        # self.stop_level = level
        self.counter = 1
        self.level = 0
        self.threading = thread_num
        self.lock = Lock()
        socket.setdefaulttimeout(10)

        self.crawled = []
        for i in range(self.threading):
            t = Thread(target=self.crawl, name="{}-thread".format(i))
            t.setDaemon(True)
            t.start()
        self.to_crawlq.join()

    # def __del__(self):
    #     time.sleep(0.5)
    #     self.to_crawlq.join()

    def crawl(self):
        while True:
            page = self.to_crawlq.get()
            if not self.check_repeating(page):
                if random.randint(0, 100)<25:
                    content = self._get_page(page)
                    # print(time.time()-self.time)
                    if (time.time()-self.time)<0.5:
                        time.sleep(1)
                    self.time = time.time()
                else:
                    self.to_crawlq.task_done()
                    if self.to_crawlq.empty():
                        break
                    continue
            else:
                content = self._get_page(page)
                # print(time.time()-self.time)
                if (time.time()-self.time)<0.5:
                    time.sleep(1)
                self.time = time.time()
                self._add_page_to_folder(content, page)
            # if not self.if_stop():#already put enough url
            links = self._get_all_links(content, page)
            for i in links:
                self.to_crawlq.put(i)
            # if page.is_end:#if it's the end of the level
            #     #with self.lock:
            #         self.level += 1
            #self.crawled.append(page)
            self.to_crawlq.task_done()
            time.sleep(2)
            if self.to_crawlq.empty():
                break


    # def if_stop(self):
    #     if self.counter >= self.stop or self.level == self.stop_level:
    #         return True
    #     else:
    #         return False

    def _get_page(self, page):
        try:
            # ip = choice(ip_addrs)
            # proxies = {"http": "http://%s" % (ip), "https": "http://%s" % (ip)}
            headers = {"User-Agent": choice(USER_AGENTS)}
            # proxy = urllib2.ProxyHandler(proxies)
            # opener = urllib2.build_opener(proxy)
            # urllib2.install_opener(opener)
            req = urllib2.Request(url=page, headers=headers)
            content = urllib2.urlopen(req).read()
            #time.sleep(2)
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

    def _get_all_links(self, content, page):
        allLinks = []
        if content == None:
            return allLinks
        soup = BeautifulSoup(content)

        recoms = soup.find("div", {"class": "recommendations-bd"})
        try:
            for movie in recoms.findAll("a"):
                link = movie.get("href","")
                if link == "":
                    continue
                link = "/".join(link.split("/")[:-1])
                if link not in allLinks:
                    allLinks.append(link)
            return allLinks
        except:
            return []

    def check_repeating(self, page):
        film_id = self.getFilenameID(page)
        if film_id in self.movie_set:
            return False
        return True

    def _valid_filename(self, s):
        import string
        valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        s = ''.join(c for c in s if c in valid_chars)
        return s

    def getFilenameID(self, filename):
        id_num = [i for i in filename if "0"<=i<="9"]
        id_num = "".join(id_num)
        return id_num

    def save_to_set(self, film_id):
        film_id = film_id.strip()
        self.movie_set.add(film_id)
        save_movie = open("crawler/save_movie.txt", "a")
        save_movie.write(film_id+"\n")
        save_movie.close()

    def _add_page_to_folder(self, content, page):
        if content == None:
            return
        folder = 'movies'  # 存放网页的文件夹
        filename = self._valid_filename(page)  # 将网址变成合法的文件名

        film_id = self.getFilenameID(page)
        if not os.path.exists(folder):  # 如果文件夹不存在则新建
            os.mkdir(folder)
        print("saving one movie: " + filename)
        f = open(os.path.join(folder, filename), 'w')
        f.write(content)  # 将网页存入文件
        f.close()
        self.save_to_set(film_id)
        self.sending_queue.put((film_id, os.path.join("movies", filename)))

if __name__ == '__main__':
    urls = [
        "https://movie.douban.com/subject/27113517/",
        "https://movie.douban.com/subject/27094896/",
        "https://movie.douban.com/subject/6053347/",
        "https://movie.douban.com/subject/26363186/",
        "https://movie.douban.com/subject/27015984/",
        "https://movie.douban.com/subject/26596361/",
        "https://movie.douban.com/subject/26420808/",
        "https://movie.douban.com/subject/26133459/",
        "https://movie.douban.com/subject/10455078/",
        "https://movie.douban.com/subject/19955955/",
        "https://movie.douban.com/subject/25757182/",
        "https://movie.douban.com/subject/24754082/",
        "https://movie.douban.com/subject/25705507/",
        "https://movie.douban.com/subject/6829661/",
        "https://movie.douban.com/subject/5153322/",
        "https://movie.douban.com/subject/6829216/",
        "https://movie.douban.com/subject/6722730/",
        "https://movie.douban.com/subject/5154001/",
        "https://movie.douban.com/subject/4117426/",
        "https://movie.douban.com/subject/3742966/",
        "https://movie.douban.com/subject/3418199/",
        "https://movie.douban.com/subject/4036518/",
        "https://movie.douban.com/subject/4093533/",
        "https://movie.douban.com/subject/4186098/",
        "https://movie.douban.com/subject/4022582/",
        "https://movie.douban.com/subject/5167833/",
        "https://movie.douban.com/subject/4312793/",
        "https://movie.douban.com/subject/3889623/",
        "https://movie.douban.com/subject/3823425/",
        "https://movie.douban.com/subject/4914616/",
        "https://movie.douban.com/subject/10617158/",
        "https://movie.douban.com/subject/3338821/",
        "https://movie.douban.com/subject/3215640/",
        "https://movie.douban.com/subject/3111355/",
        "https://movie.douban.com/subject/3872249/",
        "https://movie.douban.com/subject/2249531/",
        "https://movie.douban.com/subject/4888039/",
        "https://movie.douban.com/subject/1408100/",
        "https://movie.douban.com/subject/4057312/",
        "https://movie.douban.com/subject/3358309/",
        "https://movie.douban.com/subject/1483507/",
        "https://movie.douban.com/subject/1431685/",
        "https://movie.douban.com/subject/6557144/",
        "https://movie.douban.com/subject/1326038/",
        "https://movie.douban.com/subject/1306130/",
        "https://movie.douban.com/subject/11503638/",
        "https://movie.douban.com/subject/6985986/",
        "https://movie.douban.com/subject/5681006/",
        "https://movie.douban.com/subject/1308543/",
        "https://movie.douban.com/subject/4016948/",
        "https://movie.douban.com/subject/1428580/",
        "https://movie.douban.com/subject/4718352/",
        "https://movie.douban.com/subject/20505641/"
    ]
    movie_set = set()
    save_movie = open("crawler/save_movie.txt", "r")
    for line in save_movie.readlines():
        line = line.strip()
        movie_set.add(line)
    save_movie.close()
    sending_queue = Queue()
    myFetcher = Fetcher_movie(2,movie_set,sending_queue, urls=urls)
