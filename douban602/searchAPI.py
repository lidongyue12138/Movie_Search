#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from elasticsearch import Elasticsearch
from image_match.elasticsearch_driver import SignatureES
#连接elasticsearch
es = Elasticsearch()
ses = SignatureES(es)

index = {"index": {"_id": "26363180"}}
match_list = {u"电影名": "name", u"导演": "director", u"编辑": "editor",
u"演员": "stars", u"评分": "score", u"类型": "film_type",
 u"标签": "tag", u"年份": "time", u"地区": "district",
 u"别名": "oname", u"时长": "duration", u"海报": "img_url",u"剧情":"plot"}
# {id,index}
re_match_list = {}
for key in match_list.keys():
    re_match_list[match_list[key]]=key
# print re_match_list

class FilmInfo(object):
    def __init__(self, movie):
        # print 'Movie',movie
        self.info = movie['_source'] #movie为一个字典，想用啥用啥
        new_info = {}
        # print 'Key:', self.info.keys()
        for attr in self.info.keys():
            # print attr
            new_attr = match_list[attr]
            value = self.info[attr]
            if type(value).__name__!="unicode":
                # print 'Not unicode'
                value=unicode(str(value),"utf-8")

            new_info[new_attr]=value.decode('utf-8')
            new_info['id'] = movie["_id"]
            new_info['index'] = movie["_index"]
            new_info['match_score'] = movie.get('_score',0)
        self.info = new_info
        #得到匹配度的得分，得分越高相关度越高，大于10正确率100%，一般大于6.7可以认为匹配完成，小于6.7的基本上可以别管了


    def __str__(self):
        ret = "Movie:%s\tScore:%s\n" %(self.infoself.score)
        return ret

#精确搜索不要管评分

class ElasticSearchAPI(object):
    def __init__(self):
        self.body = {"query":{"multi_match":{"query":"五一七天乐"}}}

    def search_film(self, index='movies', doc_type='person'):
        res = es.search(index = index, doc_type = doc_type, body = self.body) #选用上述一个body进行搜索
        resp = res['hits']['hits'] #resp是一个list，包括了每个movie的信息，每个movie信息存为一个字典

        return [FilmInfo(movie).info for movie in resp]

class FilmSearch(ElasticSearchAPI):
    def __init__(self, keyword_str, search_type="fuzzy"):
        self.body = {
            "query":
            {
                "multi_match":
                {
                    "query":keyword_str,
                    "fields":["电影名.chinese"],   #搜索不同tag只需改变名字即可，如：类型.chinese
                    "operator":"and" if (search_type=="accurate") else "or"
                          #这个and表示精确搜索，去掉之后则模糊
                }
            }
        }
    def search_film(self):
        return ElasticSearchAPI.search_film(self)

class PinyinSearch(ElasticSearchAPI):
    def __init__(self, keyword_str):
        self.body = {
            "query":{
                "multi_match":{
                    "query":keyword_str,
                    "fields":["电影名.pinyin"]    #在没有合适的搜索结果时，可用拼音搜索检测模糊匹配
                        }
                    }
            }
    def search_film(self):
        return ElasticSearchAPI.search_film(self)

class TermsSearch(ElasticSearchAPI):
    def __init__(self, para_list, search_type='1', score='1'):
        bool_str = {}

        if search_type=='1': #fuzzy
            bool_str = {
            "should":
            [{"match":{para+".chinese":para_list[para]}}
                for para in para_list.keys()]}
        else:
            bool_str = {
            "must":
            [{"match":{para+".chinese":para_list[para]}}
                for para in para_list.keys()]}
        self.body = {
            "query":{"bool":bool_str}
        }
    def search_film(self):
        return ElasticSearchAPI.search_film(self)

class PlotSearch(ElasticSearchAPI):
    def __init__(self, plot):
        self.body={
            "query":{
                "multi_match":{
                    "query":plot,
                    "fields":["剧情.chinese"],
                    "operator":"and"
                        }
                    }
        }
    def search_film(self):
        return ElasticSearchAPI.search_film(self)

class PicSearch(ElasticSearchAPI):
    def __init__(self, picfile):
        self.film_list = ses.search_image(str(picfile))

    def search_film(self):
        return self.film_list

class IDSearch(ElasticSearchAPI):
    def __init__(self, film_id):
        self.film_id = film_id

    def search_film(self, index='movies', doc_type='person'):
        res = es.get( index = index, doc_type = doc_type, id=self.film_id) #选用上述一个body进行搜索
        # resp = res['hits']['hits'] #resp是一个list，包括了每个movie的信息，每个movie信息存为一个字典

        return FilmInfo(res).info
        # print resp
        # return [FilmInfo(movie).info for movie in resp]



# body_search_aggs = {
# "query":{
# "match":{
# "电影名.chinese":"灯笼"
# }
# },
# "size":10, #显示统计结果中的10个电影，若设为0，只显示统计的结果
# "aggs":{
# "aggs_name":{
# "terms":{
# "field":"电影名"
# }
# }
# }str.isdigit(
# }
# def search_pic(film_pic):
#     print ses
def main_search(film_pic):
    pass

def find_same_director(director):
    return TermsSearch({re_match_list['director']:director},search_type='2').search_film()

def find_same_district_and_time(district,time):
    print 'D&T',district,time
    attr = {re_match_list['district']:district,re_match_list['time']:int(time)}
    attr = {re_match_list['time']:1997}
    print attr
    s = TermsSearch(attr).search_film()
    print 'sss',s
    return s

def find_same_star(star_list):
    ret_list = []
    bigstars = star_list.split()[:1]
    for bs in bigstars:
        ret_list += [movie for movie in TermsSearch({u'演员':bs}).search_film()]
    # print ret_list
    return  ret_list

def chinesefy(ret_json):
    ret_json = str(ret_json).decode('utf-8')
    # print type(ret_json)
    while True:
        index = ret_json.find("u'")
        # print index
        if index==-1:break
        last = index + 2
        while ret_json[last]!="'" : last += 1
        last += 1
        # print ret_json[index:last]
        # print eval(ret_json[index:last]).decode('utf-8')
        ret_json = ret_json[:index]+"'"+eval(ret_json[index:last]).decode('utf-8')+"'"+ret_json[last:]
    return ret_json

def get_relative_film(film_id):
    # print film_id
    def tree_jsonfy(movie_list,name):
        # print movie_list
        def movie_jsonfy(movie):
            ret_json = {'name':movie["name"]}
            attr_list = ['tag','score','district','director','stars']
            ch = []
            for attr in attr_list:
                if movie.get(attr,None):
                    ch.append({"name":(str(attr)+":"+movie[attr].decode('utf-8')),"size":1})
            ret_json['children'] = ch
            return ret_json

        ret_json = {'name':name}
        ch = []
        for movie in movie_list:
            ch.append(movie_jsonfy(movie))

        ret_json['children']=ch
        print ret_json
        return ret_json

    film = IDSearch(film_id).search_film()
    # print film.keys()
    ret_json = {"name":film['name']}
    ch = []
    ch.append(tree_jsonfy(find_same_director(film['director']),u'同导演'))
    # ch.append(tree_jsonfy(find_same_district_and_time(film['district'],film['time']),'District&Time'))
    # ch.append(tree_jsonfy(find_same_tag_and_best(film['tag']),'Tag'))
    ch.append(tree_jsonfy(find_same_star(film['stars']),u'同演员'))
    ret_json['children'] = ch

    ret_json = chinesefy(ret_json)
    # print ret_json
    return ret_json

def d3barjs(movie_list):
    ret_json = []
    for movie in movie_list:
        ret_json.append(movie)
    ret_json = chinesefy(ret_json)
    print ret_json
    return ret_json

def main():
    # res = FilmSearch("宿醉",search_type="accurate").search_film()
    # for mov in res:
    #     print mov['id'], mov['name'], mov['director']
    # print PicSearch("pic/target.jpg").search_film()
    # print IDSearch('1291544').search_film()
    # print TermsSearch({u'导演':u'菲利普斯'},search_type='2').search_film()
    get_relative_film('1294007')
if __name__ == '__main__':
    main()
