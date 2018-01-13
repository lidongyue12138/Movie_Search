#-*- coding:utf-8 -*-
from elasticsearch import Elasticsearch
import  searchAPI
import os
#连接elasticsearch
es = Elasticsearch()

def research(body):
    res = es.search(index = "movies",doc_type = "person",body = body) #选用上述一个body进行搜索
    resd = res['hits']['hits'] #resp是一个list，包括了每个movie的信息，每个movie信息存为一个字典
    for movie in resd:
        for item in movie['_source']:
            print item, movie['_source'][item]
        print '\n'
    return resd


def recommend(key_list):
    should = []
    should.append({"term":{"导演.chinese" : key_list[u'导演']}})
    should.append({"term": {"年份": key_list[u'年份']}})
    should.append({"term": {"演员.chinese": key_list[u'演员']}})
    should.append({"term": {"地区": key_list[u'地区']}})
    should.append({"term": {"类型.chinese": key_list[u'类型']}})
    body_search_terms = {"query":{"bool":{"should":should}}}
    return research(body_search_terms)
