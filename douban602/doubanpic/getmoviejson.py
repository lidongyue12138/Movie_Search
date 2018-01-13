# -*- coding: UTF-8 -*-
import json

def get_ok_list():
    ok_file = open("hash.txt",'r')
    q = ok_file.readlines()
    # print q
    ret = [int(line.split()[0]) for line in q]
    ok_file.close()
    return ret

def get_json():

    movie_file = open("movie.json",'r')
    movie = movie_file.readlines()

    index = 0
    movie_info = {}
    url_list = {}
    for line in movie:
        line = line.decode('utf-8')
        j = json.loads(line)
        
        if 'index' in j.keys():
            index = int(j['index']['_id'])
            # print index
        else:
            movie_info[index] = j
            url_list[index]=movie_info[index][u'海报']
            # for info in j.keys():
            #     print info, movie_info[index][info]
            # print index, movie_info[index][u'海报']
    
    return url_list
def main():
    get_json()

if __name__ == '__main__':
    main()