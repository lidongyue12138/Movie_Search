from elasticsearch import Elasticsearch

#连接elasticsearch
es = Elasticsearch()

class FilmSearch():

    body = {
        "query":
        {
            "multi_match":
            {
                "query":"你要搜的内容",
                "fields":["电影名.chinese"],   #搜索不同tag只需改变名字即可，如：类型.chinese
                "operator":"and"       #这个and表示精确搜索，去掉之后则模糊
            }
        }
}

body_search_pinyin = {
"query":{
"multi_match":{
"query":"你要搜的内容",
"fields":["电影名.pinyin"]    #在没有合适的搜索结果时，可用拼音搜索检测模糊匹配
}
}
}

body_search_terms = {
"query":{
"bool":{
"should":{
"term":{
"电影名.chinese":"你要搜的内容1"
}
},
"should":{
"term":{
"标签.chinese":"你要搜的内容2"  #term项可以无限添加，采用should逻辑就是至少有一个match就能视为结果，越多相关度越高。must精确匹配
}
}
}
}
}

body_search_aggs = {
"query":{
"match":{
"电影名.chinese":"灯笼"
}
},
"size":10, #显示统计结果中的10个电影，若设为0，只显示统计的结果
"aggs":{
"aggs_name":{
"terms":{
"field":"电影名"
}
}
}
}

res = es.search(index = "movies",doc_type = "person",body = choosed_body) #选用上述一个body进行搜索
resp = res['hits']['hits'] #resp是一个list，包括了每个movie的信息，每个movie信息存为一个字典

#得到所有片子的信息
for movie in resp:
    print movie['_source']['电影名'] #movie为一个字典，想用啥用啥
    print movie['_score'] #得到匹配度的得分，得分越高相关度越高，大于10正确率100%，一般大于6.7可以认为匹配完成，小于6.7的基本上可以别管了

def search_film(kwd,):
    #kwd 格式
    # {'name': (film_name), 'type': (film_type), 'director': (director), 'star': (star),
    # 'score': 'best'/'worst, 'time': film_time， search_type: "accurate"/"fuzzy" }
    # 其中，score 的best返回评分高于一定阈值的好片，worst为“搜烂片”功能
    # 
    # search_type : accurate:精确搜索/ fuzzy:模糊搜索

    pass
    # return film_list
    
    # film_list = [{},{},{},{}]
    # Sorted

def search_plot(film_plot):
    #搜剧情，默认为模糊搜索

    #film_list = [{},{},{},{}]
    #Sorted

    pass
    # return film_list

def search_pic(film_pic):
    # 搜海报，mbj自己做
    pass

