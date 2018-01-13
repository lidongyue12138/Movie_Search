#-*- coding:utf-8 -*-
from elasticsearch import Elasticsearch
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

def recommend(key_list):
    f = open('data.py', 'w')
    f.write('#-*- coding:utf-8 -*-')
    f.write('\n')

    f.write('body_search_terms = {"query": {"bool": {"should": {"term": {"')
    f.write('导演')
    f.write('.chinese": "')
    f.write(key_list[u'导演'].encode('utf8'))
    f.write('"}}')

    f.write(',"should": {"term": {"')
    f.write('年份')
    f.write('": "')
    f.write(key_list[u'年份'].encode('utf8'))
    f.write('"}}')

    for i in range(3):
        if i + 1 > len(key_list[u'演员']):
            break
        f.write(',"should": {"term": {"')
        f.write('演员')
        f.write('.chinese": "')
        f.write(key_list[u'演员'].split()[i].encode('utf8'))
        f.write('"}}')

    f.write(',"should": {"term": {"')
    f.write('地区')
    f.write('": "')
    f.write(key_list[u'地区'].encode('utf8'))
    f.write('"}}')

    for t in key_list[u'类型'].split():
        f.write(',"should": {"term": {"')
        f.write('类型')
        f.write('.chinese": "')
        f.write(t.encode('utf8'))
        f.write('"}}')

    f.write('}}}')
    f.close()
    import data
    research(data.body_search_terms)
    os.remove('data.py')

#key_list是一部电影的搜索结果的['_source']
