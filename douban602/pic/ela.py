from elasticsearch import Elasticsearch
from image_match.elasticsearch_driver import SignatureES
import os
import time
es = Elasticsearch()
ses = SignatureES(es)

start = time.clock()
# pic_list = {}
count = 0
for dirpath, dirnames, filenames in os.walk("./data"):
    # print dirpath, dirnames, filenames
    for filename in filenames:
        try:
            ses.add_image('data/'+filename)
            print filename
            count += 1
            print count, time.clock()-start
            # if count==2000: break
        except:
            continue

print ses.search_image('target.jpg')
