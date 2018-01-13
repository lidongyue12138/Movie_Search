#READ ME
'''In this program, all the pinyin(xia hua xian) are showed by -'''
import pyes
from elasticsearch import Elasticsearch

#connecting elasticsearch
es = pyes.ES('localhost:9200')

#define mapping
mapping ={
"mappings":{
            "person":{
                "properties":{
                    "电影名":{
                        "type":"text",
                        "fields":{
                            "pinyin":{
                                "type":"text",
                                "analyzer":"ik-smart",
                                "search_analyzer":"ik-smart"},
                            "chinese":{
    "type":"text",
    "analyzer":"ik-index",
    "search_analyzer":"ik-index"
    }
        }
    },
    "导演":{
        "type":"text",
    "fields":{
    "pinyin":{
    "type":"text",
    "analyzer":"ik-smart",
    "search_analyzer":"ik-smart"},
    "chinese":{
    "type":"text",
    "analyzer":"ik-index",
    "search_analyzer":"ik-index"
    }
    }
    },
    "编辑":{
    "type":"text",
    "fields":{
    "pinyin":{
    "type":"text",
    "analyzer":"ik-smart",
    "search_analyzer":"ik-smart"},
    "chinese":{
    "type":"text",
    "analyzer":"ik-index",
    "search_analyzer":"ik-index"
    }
    }
    },
    "演员":{
    "type":"string",
    "fields":{
    "pinyin":{
    "type":"string",
    "analyzer":"ik-smart",
    "search_analyzer":"ik-smart"},
    "chinese":{
    "type":"string",
    "analyzer":"ik-index",
    "search_analyzer":"ik-index"
    }
    }
    },
    "评分":{
        "type":"double",
        "index":"not_analyzed"
                    },
    "类型":{
    "type":"text",
    "fields":{
    "pinyin":{
    "type":"text",
    "analyzer":"ik-smart",
    "search_analyzer":"ik-smart"},
    "chinese":{
    "type":"text",
    "analyzer":"ik-index",
    "search_analyzer":"ik-index"
    }
    }
    },
    "标签":{
    "type":"text",
    "fields":{
    "pinyin":{
    "type":"text",
    "analyzer":"ik-smart",
    "search_analyzer":"ik-smart"},
    "chinese":{
    "type":"text",
    "analyzer":"ik-index",
    "search_analyzer":"ik-index"
    }
    }
    },
    "年份":{
        "type":"string",
        "index":"not_analyzed"
                    },
    "地区":{
    "type":"text",
    "fields":{
    "pinyin":{
    "type":"text",
    "analyzer":"ik-smart",
    "search_analyzer":"ik-smart"},
    "chinese":{
    "type":"text",
    "analyzer":"ik-index",
    "search_analyzer":"ik-index"
    }
    }
    },
    "别名":{
    "type":"text",
    "fields":{
    "pinyin":{
    "type":"text",
    "analyzer":"ik-smart",
    "search_analyzer":"ik-smart"},
    "chinese":{
    "type":"text",
    "analyzer":"ik-index",
    "search_analyzer":"ik-index"
    }
    }
    },
    "时长":{
        "type":"string",
        "index":"not_analyzed"
                    }
    
    }
    }
    },
"settings":{
    "analysis":{
        "filter":{
            "local_synonym":{
                "type":"synonym",
                "synonyms_path":"analysis/synonym.txt"
            }
        },
"analyzer":{
    "ik-smart":{
        "type":"custom",
        "tokenizer":"pinyin",
        "filter": [
        "local_synonym"
        ]
    },
    "ik-index":{
        "type":"custom",
        "tokenizer":"ik_max_word",
        "filter":[
        "local_synonym"
        ]
        }
    }
    }
}

#create an index and put mapping into elasticsearch
es.create-index("movies")
es.put-mapping("movie",{"properties":mapping},["movies"])

#put a new json into the index,json-file is founded by reading the new json file
data = json.dumps(json-files)
es.index({})#you just put the right data into the right place
es.refresh()

#these are about searching
#example:searching for 五一七天乐
body = {
"query":{
"match":{
"电影名.chinese":"五一七天乐"
}
}
}

res = es.search(index = "movies",doc_type = "person", body = body)
'''about res
    res['hits']['hits'] is a list contains the movies that are matched.
    resp = res['hits']['hits'][0] ------------------------the first matched movie
    resp['_score'] -----------------------degree of association
    NOTE:If resp['_score'] > 7,it's matched. If no one satisfy the condition, use indistinct search
    resp["电影名"] ...... ----------------------information of matched movies'''

#change body and we can get several different search style
#multi_search
body = {
"query":{
"multi_match":{
"query":"毕福剑",
"fields":["导演.chinese","演员.chinese"],
"operator":"and"
}
}
}

#indistinct search for actor 毕福剑
body = {
"query":{
"multi_match":{
"query":"毕福剑",
"fields":["演员.pinyin","演员.chinese"],
"operator":"and"
}
}
}
    
#for more function, please find Quan Luo
    
    
    
    
    
    
    
    
    
    
                                  

