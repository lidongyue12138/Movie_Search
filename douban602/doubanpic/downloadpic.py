# -*- coding: UTF-8 -*-
import requests
import time
import json
import os
import numpy as np
import matplotlib.image as mpimg
from io import BytesIO
from PIL import Image
from match_hash import get_hash,match
from getmoviejson import get_json, get_ok_list

def get_id():
    pass

to_do_list = []
ok_list = []
ok_num = 0

to_save_list = {}

start_time = time.clock()
last_time = time.clock()


def save_to_file():
    global to_save_list
    if not os.path.exists('hash.txt'):
        f = open('hash.txt','w')
        f.close()

    f = open('hash.txt','at')
    for index in to_save_list:
        f.write("%s %s %s\n" % (index,to_save_list[index][0],to_save_list[index][1]))
        
        
        # to_do_list.remove(index)
        # ok_list.append(index)
    f.close()
    to_save_list = {}

def save_hash_result(index,hash1,hash2):
    global to_save_list
    to_save_list[index]=[hash1,hash2]
    
    if len(to_save_list)>100:
        save_to_file()
        # save result in batch, in order to save time
        
    print 'Save %s ok' %(index)


def download_onepic(url,index):
    global last_time
    global ok_num
    global ok_list

    try:
        if time.clock()-last_time<1:
            time.sleep(0.5)
        r = requests.get(url)
    except Exception as e:
        print e

    ok_list.append(index)
    ok_num += 1
    last_time = time.clock()
    print "Ok_num",ok_num 
    print "Download Pic %s. Index %s, Time %s" %(ok_num, index, last_time-start_time)
    img_file = r.content

    try:
        f = open(str(index)+".jpg","wb")
        f.write(r.content)
        f.close()
    except Exception as e:
        print "Pic File IO failed"
        print e
    return r.content


def playground(img):
    w,h,c = img.shape
    for i in range(h):
        print img[h,:]

def main():

    global to_save_list

    f_exception = open('exception.txt','at')
    f_complete = open('complete.txt','at')


    url_list = get_json()
    ok_list = get_ok_list()
    # print ok_list
    # return 
    # url_list = {1:"https://img1.doubanio.com/view/movie_poster_cover/lpst/public/p1910812549.jpg"}
    to_do_list = url_list.keys()
    for index in to_do_list:
        # print index
        # print index in ok_list
        print 'Now deal with %s' %(index)
        if index in ok_list:
            print "Already Done."
            continue
        try:
            img_binfile = download_onepic(url_list[index],index)
            
            img_raw = Image.open(BytesIO(img_binfile))
            img=np.asarray(img_raw)
            # print img
            # playground(img)
            hash1, hash2 = get_hash(img)
            print '%s: hash1 %s \t hash2 %s' %(index,bin(hash1),bin(hash2))
            
            save_hash_result(index,hash1,hash2)
    
        except Exception as e:
            f_exception.write("%s %s\n"%(index,e))
            print index,"Failed."
            print e

    if len(to_save_list)>0:
        save_to_file()
    f_exception.close()
    f_complete.close()
    print ok_num

if __name__ == '__main__':
    main()
