# coding: utf-8
import os
import sys
sys.setrecursionlimit(10000)
from configure import urls
from crawler.crawler_douban import Fetcher_movie
from crawler.crawler_review import Fetcher_review
from parser.parse_review import review_parser
from parser.parser import parser_for_movie
from search.save_to_elasticsearch import elasticsearch_douban
from elasticsearch import Elasticsearch

from multiprocessing import Queue, Process

def getFilenameID(filename):
    id_num = [i for i in filename if "0"<=i<="9"]
    id_num = "".join(id_num)
    return id_num
#main_part

movie_queue = Queue()
to_fetch_review_queue = Queue()
review_queue = Queue()

put_movie_to_search_queue = Queue()
put_cele_to_search_queue = Queue()
put_review_to_search_queue = Queue()

#initing...
movie_set = set()
save_movie = open("crawler/save_movie.txt", "r")
for line in save_movie.readlines():
    line = line.strip()
    movie_set.add(line)
save_movie.close()

review_set = set()
save_review = open("crawler/save_review.txt", "r")
for line in save_review.readlines():
    line = line.strip()
    review_set.add(line)
save_review.close()

reviews = open("review.txt", "r")
for line in reviews.readlines():
    to_fetch_review_queue.put(line)
reviews.close()

for filename in os.listdir("movies"):

    filename = os.path.join("movies", filename)
    id_num = getFilenameID(filename)
    #time.sleep(1)
    if movie_queue.full():
        time.sleep(0.1)
    else:
        movie_queue.put((id_num, filename))

for filename in os.listdir("reviews"):

    filename = os.path.join("reviews", filename)
    id_num = getFilenameID(filename)
    try:
        review_queue.put((id_num, filename), block = False)
    except:
        continue

es = Elasticsearch()

#starting...
movieFetcher = Process(target=Fetcher_movie, args=(1, movie_set, movie_queue, urls))
movieParser = Process(target=parser_for_movie, args=(movie_queue, to_fetch_review_queue,\
                                        put_movie_to_search_queue, put_cele_to_search_queue))
reviewFetcher = Process(target=Fetcher_review, args=(to_fetch_review_queue, review_queue, review_set))
reviewParser = Process(target=review_parser, args=(review_queue,put_review_to_search_queue,\
                                                    review_set))
saveToSearch = Process(target=elasticsearch_douban, args=(es, put_movie_to_search_queue,\
                                                        put_cele_to_search_queue,\
                                                        put_review_to_search_queue))
movieFetcher.start()
movieParser.start()
reviewFetcher.start()
reviewParser.start()
saveToSearch.start()
