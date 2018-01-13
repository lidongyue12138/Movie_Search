# import cv2
import os
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
from PIL import Image

dist = []
def one_vec(img):
    def get_onebit(x):
        if x<0.3: return 0
        if x>0.38: return 2
        return 1

    h, w, col = tuple(img.shape)
    color_bin = [0,0,0]
    for i in [0,1,2]:
        color_bin[i] = img[:,:,i].sum()

    # print color_bin
    all_color = sum(color_bin)
    ret = ''
    for i in [0,1,2]:
        # dist.append(float(color_bin[i])/all_color)
        this_hash = get_onebit(float(color_bin[i])/all_color)
        ret = ret + this_hash *'1'+ (2-this_hash)*'0'
    # print ret
    ret = int(ret,base=2)
    # print ret        
    return ret

def calc_hash1(img):
#Calculate the color-vector of a Picture
#We use the method of bit operation
# use lsh [0,1,2,0,1,2] = 001011001011
# d=12 c=2; so 24 bit at all
    vector_bit = 0

    height, width, col = tuple(img.shape)
    h1 = img[0:height/2,0:width/2,:]
    h2 = img[height/2:height,0:width/2,:]
    h3 = img[0:height/2,width/2:width,:]
    h4 = img[height/2:height,width/2:width,:]
    # h1|h3
    # -----
    # h2|h4
    vector_bit = vector_bit<<6 | one_vec(h1)
    vector_bit = vector_bit<<6 | one_vec(h2)
    vector_bit = vector_bit<<6 | one_vec(h3)
    vector_bit = vector_bit<<6 | one_vec(h4)
    return vector_bit
    #b,g,r

def calc_hash2(img):
# get focus-center color distribution & brightness
# 6+5 
    def getbright(ave):
        # c=6 ,5 bit
        if ave<0.4 :return 0
        if ave<0.475: return 1
        if ave<0.55: return 2
        if ave<0.625: return 3
        if ave<0.7: return 4
        return 5
    h, w, col = tuple(img.shape)
    center = img[h/4:h*3/4, w/4:w*3/4, :]

    # return calc_hash1(center)
    ret = one_vec(center)

    #brightness 5 bit
    h, w, col = tuple(center.shape)
    col_sum = center.sum()
    col_sum = float(col_sum)/3/h/w/255
    dist.append(col_sum)
    # print col_sum
    x = getbright(col_sum)
    # print x
    ret = (ret<<5) | int(x*'1'+(5-x)*'0',base=2)
    # print bin(ret)
    return ret

def get_hash(img):
    height, width, col = tuple(img.shape)
    hash1 = calc_hash1(img)
    hash2 = calc_hash2(img)
    return hash1,hash2

def getones(x):
    ret = 0 
    while x>0:
        ret += x&1
        x = x>>1
    return ret

def match(hash1,hash2,img):
    this_hash1 = calc_hash1(img)
    this_hash2 = calc_hash2(img)
    match1_list = {}
    threshold = 5
    for key1 in hash1.keys():
        s1 = getones(key1^this_hash1)
        if s1 < threshold:
            for pic in hash1[key1]:
                match1_list[pic] = s1

    match2_list = {}
    for key2 in hash2.keys():
        s2 = getones(key2^this_hash2)
        if s2 < threshold:
            for pic in hash2[key2]:
                match2_list[pic] = s2

    p1 = match1_list.keys()
    p2 = match2_list.keys()
    total_match = {}
    for p in p1:
        if p in p2:
            total_match[p] = (2*match1_list[p])**2 + (2*match2_list[p])**2
    
    
    total_match = sorted(total_match.iteritems(),key = lambda d:d[1])
    return total_match

# def show_result(target_img,pic_list):
    # target_img = convertColorSpace(target_img)
    # plt.subplot(241)
    # plt.imshow(target_img)

    # index = 4
    # for pic in pic_list[:4]:
    #     index += 1
    #     plt.subplot(2,4,index)
    #     img = cv2.imread('dataset/'+pic[0])
    #     img = convertColorSpace(img)
    #     plt.imshow(img)
    #     print 'diff='+str(pic[1])
    #     plt.title('diff='+str(pic[1]))
    # plt.show()

if __name__ == '__main__':
    # hash1,hash2 = getindex()
    import sys
    hash1, hash2 =getindex_precalc()

    target = cv2.imread('target.jpg')

    if len(sys.argv)>1:
        print sys.argv[1]
        if '.jpg' in sys.argv[1]:
            target = cv2.imread('dataset/'+sys.argv[1])
    pic_list = match(hash1,hash2,target)
    show_result(target,pic_list)

    # print dist
    # plt.hist(dist,bins=40)
    # plt.show()
    # test_list = ['27.jpg','35.jpg','16.jpg']
    # for imgname in test_list:
    #     img = cv2.imread('dataset/'+imgname)
    #     calc_hash2(img)

