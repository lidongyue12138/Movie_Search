from image_match.goldberg import ImageSignature
gis = ImageSignature()
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os
from numpy import array, int8
import time
# start = time.clock()
# pic_list = {}
# count = 0
# for dirpath, dirnames, filenames in os.walk("./data"):
#     # print dirpath, dirnames, filenames
#     for filename in filenames:
#         try:
#             print filename
#             count += 1
#             print count, time.clock()-start
#             # if count==2000: break
#             pic_list[filename]=gis.generate_signature("./data/"+filename)
#         except:
#             continue
# f = open("data.txt",'w')
# f.write(str(pic_list))
# f.close()
# #

def match_pic(pic_file):
    f = open("data.txt",'r')
    g = f.read()
    start = time.clock()
    pic_list = eval(g)
    print "Read File Time", time.clock()-start
    print len(pic_list)
    # for j in g.keys():
    #     print g[j]
    ans = []
    target_hash = gis.generate_signature(pic_file)
    for p in pic_list.keys():
        dist = gis.normalized_distance(pic_list[p], target_hash)
        if dist < 0.5:
            ans.append( (p, dist) )
    ans = sorted(ans,key=lambda b:b[1])
    # print ans[0][0]
    ans = ans[:10]
    return ans
    # for pic in ans:
    #     img = mpimg.imread('data/'+pic[0])
    #     plt.imshow(img)
    #     plt.show()



if __name__ == '__main__':
    print match_pic("target.jpg")
