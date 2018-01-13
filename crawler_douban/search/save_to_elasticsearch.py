# coding: utf-8
import pyes
from elasticsearch import Elasticsearch
import json
from threading import Thread, Lock, stack_size

from multiprocessing import Queue, Process

def test(q):
    m = {"电影名": "功夫", "导演": "周星驰", "编辑": "曾瑾昌  陈文强  周星驰  霍昕", "演员": "周星驰  元秋  元华  黄圣依  梁小龙  陈国坤  田启文  林子聪  林雪  冯克安  释彦能  冯小刚  袁祥仁  张一白  赵志凌  董志华  何文辉  陈凯师  贾康熙  林子善  任珈锐  王仕颖", "评分": 7.9, "类型": "喜剧  动作  犯罪  奇幻", "标签": "周星驰 喜剧 香港 功夫 动作 香港电影 搞笑 电影", "年份": "2004", "地区": "中国大陆  香港", "别名": "功夫3D  Kung Fu Hustle", "时长": "100分钟(3D重映)  95分钟(中国大陆)  99分钟(美国)", "海报": "https://img1.doubanio.com/view/photo/s_ratio_poster/public/p2219011938.jpg", "剧情": "　　1940年代的上海，自小受尽欺辱的街头混混阿星（周星驰）为了能出人头地，可谓窥见机会的缝隙就往里钻，今次他盯上行动日益猖獗的黑道势力“斧头帮”，想借之大名成就大业。\n                                    \n                                　　阿星假冒“斧头帮”成员试图在一个叫“猪笼城寨”的地方对居民敲诈，不想引来真的“斧头帮”与“猪笼城寨”居民的恩怨。“猪笼城寨”原是藏龙卧虎之处，居民中有许多身怀绝技者（元华、梁小龙等），他们隐藏于此本是为远离江湖恩怨，不想麻烦自动上身，躲都躲不及。而在观战正邪两派的斗争中，阿星逐渐领悟功夫的真谛。"}
    q.put((1315790, m))

class elasticsearch_douban:
    def __init__(self, es, movie_queue, cele_queue, review_queue):
        self.es = es
        self.movie_queue = movie_queue
        self.cele_queue = cele_queue
        self.review_queue = review_queue

        movie_thread = Thread(target=self.save_movies, name="movie")
        cele_thread = Thread(target=self.save_celes, name="celes")
        review_thread = Thread(target=self.save_reviews, name="reviews")


        movie_thread.start()
        cele_thread.start()
        review_thread.start()

        movie_thread.join()

    def save_movies(self):
        while (True):
            try:
                movie_id, movie = self.movie_queue.get()
            except:
                continue

            self.save_to_movie(movie_id, movie)

    def save_celes(self):
        while (True):
            try:
                cele_id, celebrity = self.cele_queue.get()
            except:
                continue

            self.save_to_cele(cele_id, celebrity)

    def save_reviews(self):
        while (True):
            try:
                review_id, review = self.review_queue.get()
            except:
                continue

            self.save_to_review(review_id, review)





    def save_to_movie(self, id_num, content):
        res = self.es.index(index="movies", doc_type='person', id=id_num, body=content)
        print("version_movie:" + str(res["_version"]))

    def save_to_cele(self, id_num, content):
        res = self.es.index(index="celebrity", doc_type='celes', id=id_num, body=content)
        print("version_cele:" + str(res["_version"]))

    def save_to_review(self, id_num, content):
        res = self.es.index(index="comment", doc_type='com', id=id_num, body=content)
        print("version_review:" + str(res["_version"]))

if __name__ == '__main__':
    q1 = Queue()
