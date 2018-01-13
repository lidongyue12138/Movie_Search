# coding=utf-8
from bs4 import BeautifulSoup
from collections import defaultdict
import re
import json
import os
from collections import OrderedDict

from multiprocessing import Queue, Process

class review_parser:
    def __init__(self, queue, put_to_review_queue ,review_set):
        self.queue = queue
        self.review_set = review_set
        self.put_to_review_queue = put_to_review_queue
        while (True):
            try:
                id_num, filename = self.queue.get(block = False)
            except:
                continue
            try:
                f = open(filename, "r")
                soup = BeautifulSoup(f)
                #time.sleep(1)
                f.close()
            except:
                continue

            try:
                movie = self.parse_movie(soup)
                title, review = self.parse_review(soup)
            except:
                continue
            self.save_review(movie, title, review, id_num)

            os.remove(filename)
            self.save_to_set(id_num)

    def save_to_set(self, id_num):
        id_num = id_num.strip()
        self.review_set.add(id_num)
        save_review = open("crawler/save_review.txt", "a")
        save_review.write(id_num+"\n")
        save_review.close()

    def parse_movie(self, soup):
        content = soup.find("header", {"class", "main-hd"})
        movie_tag = content.findAll("a")[1]
        movie = movie_tag.get_text().encode("utf-8")
        return movie

    def parse_review(self, soup):
        content = soup.find("div", {"id" : "content"})
        title = content.find("h1").get_text()
        title = title.encode("utf-8")

        review = content.find("div", {"class": "review-content clearfix"}).get_text()
        review = review.encode("utf-8")

        return title, review
    def save_review(self, movie, title, content, id_num):
        # filename = "jsonData/review.json"
        # f = open(filename, "a")
        review = {
            "电影名": movie,
            "评论标题": title,
            "评论内容": content
        }
        # id_json = {"index": {"_id":id_num}}
        # json.dump(id_json, f, ensure_ascii=False)
        # f.write("\n")
        # json.dump(review, f, ensure_ascii=False)
        # f.write("\n")
        # f.close()
        while True:
            if self.put_to_review_queue.full():
                continue
            else:
                self.put_to_review_queue.put((id_num, review))
                break
        print("save one review to search!")


if __name__ == '__main__':
    q = Queue()
    writer = Process(target=pass_review_data, args=(q,))
    writer.start()

    reader = Process(target=review_parser, args=(q,))
    reader.start()

    reader.join()
    writer.join()
