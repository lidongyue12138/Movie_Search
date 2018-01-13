#-*- coding:utf-8 -*-
from BeautifulSoup import BeautifulSoup
import urllib2
import re
import urlparse
import os
import urllib
import sys
import socket
import threading
import Queue
import time
import codecs
from splinter import Browser
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import selenium.webdriver.support.ui as ui

def add_thread():
    global threads
    if threading.active_count() < 20:
        for i in range(50 - threading.active_count()):
            thread = threading.Thread(target=no_error_contents)
            threads.append(thread)
            thread.setDaemon(True)
            thread.start()

def valid_filename(s):
    import string
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    s = ''.join(c for c in s if c in valid_chars)
    return s

def get_links(safari):
    links = []
    filmtitle = safari.find_elements_by_class_name('op_exactqa_item c-gap-bottom c-span6 ')
    for item in range(8):
        i = filmtitle[item]
        content = i.text
        mark = re.sub(u'[　, ]', u'', content)[-6:]
        #print title, mark, '\n'
        linkurl = i.find_elements_by_xpath('//*[@id="1"]/div/div[1]/div[2]/div[1]/div/p[1]/a')[item]
        link = linkurl.get_attribute('href')
        title = linkurl.get_attribute('title')
        imgurl = i.find_elements_by_xpath('//*[@id="1"]/div/div[1]/div[2]/div[1]/div/p[1]/a/img')[item].get_attribute('src')
        links.append([title, mark, link, imgurl])
    return links

def choose_type(n): #n从0到967
    a = n % 8
    p = ((n - a) // 8) % 11
    t = (n - a - 8 * p) // 88
    return [t, p, a]

def get_type_films(safari, n):#差一个异常处理
    films = get_links(safari)
    btn = safari.find_element_by_class_name('opui-page-next OP_LOG_BTN')
    count = 0
    try:
        while btn.is_displayed():
            count += 1
            btn.click()
            time.sleep(0.4)
            if count % 10 == 0:
                time.sleep(1)
            films += get_links(safari)
            btn = safari.find_element_by_class_name('opui-page-next OP_LOG_BTN')
    except IndexError:#将未爬完的页面记录
        print 'page', n, 'error'
        error_list.append(n * 1000 + count)
        add_link_to_folder(films)
        #return films
    add_link_to_folder(films)
    #return films
def add_link_to_folder(films):
    folder = 'links'
    if not os.path.exists(folder):
        os.mkdir(folder)
    for film in films:
        title = film[0]
        mark = film[1]
        link = film[2]
        imgurl = film[3]
        filename = '%s.txt' % (title)
        f = open(os.path.join(folder, filename), 'w')
        #print mark, link, imgurl
        f.write(mark.encode('utf') + '\n' + str(link) + '\n' + str(imgurl))
        f.close()
def add_page_to_folder(item):  # 将网页存到文件夹里，将网址和对应的文件名写入index.txt中
    folder = 'films'  # 存放网页的文件夹
    if not os.path.exists(folder):  # 如果文件夹不存在则新建
        os.mkdir(folder)
    if len(item) <= 3:
        return
    name = item[0]
    img = item[1]
    url = item[2]
    content = item[3]
    anothername = item[4]
    #print item
    filename = name
    f = open(os.path.join(folder, filename), 'w')
    #print type(anothername), type(img), type(content)
    if anothername == '':
        f.write(anothername + '\n' + img.encode('utf') + '\n' + content.encode('utf'))
    else:
        f.write(anothername.encode('utf') + '\n' + img.encode('utf') + '\n' + content.encode('utf'))
    f.close()


def find_baike_contents(link, name, url_img):#需要在函数外写try,应返回[名字, 图片，网址，内容，别名(没有则返回空字符串)]
    result = [name, url_img]
    film_content = ''
    link = link[:4] + link[5:]
    content = urllib2.urlopen(link, timeout = 10).read()
    content = BeautifulSoup(content)
    baikelink = content.find('div', {'mu': re.compile('^https:\/\/baike\.baidu\.com\/item\/')})
    result.append(baikelink)
    if baikelink == None:
        return ['', '']
    baikelink = baikelink.find('a')
    baikecontent = urllib2.urlopen(baikelink['href']).read()
    baikecontent = BeautifulSoup(baikecontent)
    contents_begin = baikecontent.find('h2', {'class': 'title-text'})
    contents_begin_div = contents_begin.parent
    temp_point = contents_begin_div.nextSibling.nextSibling
    while temp_point['class'] == 'para':
        film_content += temp_point.text
        #print temp_point.text
        temp_point = temp_point.nextSibling.nextSibling
    result.append(film_content)

    another_name_tag = baikecontent.findAll('dt', {'class': 'basicInfo-item name'})
    another_name = ''
    for i in another_name_tag:
        if (i.text) == u'\u5176\u4ed6\u540d\u79f0':
            another_name = i.nextSibling.nextSibling.text
            break
    #print another_name
    result.append(another_name)
    return result

def no_error_contents():
    global q
    global error_links
    global totle
    while q.empty() != True:
        film = q.get()
        content = []
        try:
            content = find_baike_contents(film[3], film[0], film[4])
            add_page_to_folder(content)
            totle += 1
            #print totle, 'success', film[0]
        except socket.timeout:
            print 'timeout', film[0]
            print '还剩下进程数：', threading.active_count()
            add_thread()
            error_links.append([film[0], film[3], film[4]])
        except AttributeError:
            print 'linkerror', film[0]
            print '还剩下进程数：', threading.active_count()
            add_thread()
            error_links.append([film[0], film[3], film[4]])
        except:
            print 'other_error', film[0]
            print '还剩下进程数：', threading.active_count()
            add_thread()
            error_links.append([film[0], film[3], film[4]])
        if varlock.acquire():
            #缺去重if bllomfilter(content):
            #print threading.currentThread().getName()
            #final_contents.append(content)
            varlock.release()
            time.sleep(1)

def find_all_contents(films):#多线程
    contents = []
    global q
    global error_links

    for film in films:
        q.put(film)

    while len(error_links) != 0:
        print len(error_links)
        for link in error_links:
            try:
                final_contents.append([find_baike_contents(link[1], link[0], link[4])])
            except socket.timeout:
                print 'timeout'
                print '还剩下进程数：', threading.active_count()
                add_thread()
            except AttributeError:
                print 'linkerror'
                print '还剩下进程数：', threading.active_count()
                add_thread()
            except:
                print 'othererror'
                print '还剩下进程数：', threading.active_count()
                add_thread()
            error_links.remove(link)
    #print contents

#返回[名字， 图片， 内容， 别名]的列表
def deal_with_errors(error_position, films, new_safari):
    error_list.remove(error_position)
    position = choose_type(error_position)
    t = position[0]
    p = position[1] + 11
    a = position[2] + 22
    btn = new_safari.find_elements_by_class_name('op_exactqa_tag_item OP_LOG_BTN ')
    btn[t].click()
    btn[p].click()
    btn[a].click()
    time.sleep(1)
    films += get_type_films(new_safari, error_position)


def get_all_links(page_num):
    global safari
    film_content = []
    global q
    global error_links
    error_links = []
    type_list = choose_type(page_num)
    t = type_list[0]
    p = type_list[1] + 11
    a = type_list[2] + 22
    btn = safari.find_elements_by_class_name('op_exactqa_tag_item OP_LOG_BTN ')
    btn[t].click()
    btn[p].click()
    btn[a].click()
    time.sleep(2)
    get_type_films(safari, page_num)#films为一个存储若干电影信息[标题，评分，百度搜索结果链接，图片链接]的列表
    '''for j in range(NUM):
        t = threading.Thread(target=no_error_contents)
        threads.append(t)
    for thread in threads:
        thread.setDaemon(True)
        thread.start()
    print threading.current_thread().getName()'''
    print 'page', page_num, 'ready'
    '''find_all_contents(films)#在films中提取出来link，返回百科的电影简介,多线程
#缺去重
    #add_page_to_folder(final_contents)
    for line in threads:
        line.join()'''

if __name__ == '__main__':
    NUM = 100
    global error_list
    global final_contents
    error_links = []
    totle = 0
    q = Queue.Queue()
    varlock = threading.Lock()
    final_contents = []
    error_list = []#得到的数为类型数（n）*1000+断页数
    threads = []
    '''page = 'https://www.baidu.com/s?wd=%E7%94%B5%E5%BD%B1'
    safari = webdriver.Safari()
    safari.get(page)
    safari.maximize_window()
    nouse_page = [57, 58, 59, 60, 61, 62, 63, 113, 114, 115, 116, 117, 118, 119 ,121, 122, 123, 124, 125, 126, 127, 129, 130, 131, 132, 133, 134, 135, 145, 146, 147, 148, 149, 150, 151,
153, 154, 155, 156, 157, 158, 159, 161, 162, 163, 164, 165, 166, 167, 209, 210, 211, 212, 213, 214, 215, 217, 218, 219, 220, 221, 222, 223, 233, 234, 235, 236, 237, 238, 239, 297, 298, 299, 300, 301, 302, 303,
305, 306, 307, 308, 309, 310, 311, 321, 322, 323, 324, 325, 326, 327, 329, 330, 331, 332, 333, 334, 335, 337, 338, 339, 340, 341, 342, 343, 409, 410, 411, 412, 413, 414, 415, 457, 458, 459, 460, 461, 462, 463,
465, 466, 467, 468, 469, 470, 471, 473, 474, 475, 476, 477, 478, 479, 481, 482, 483, 484, 485, 486, 487, 489, 490, 491, 492, 493, 494, 495, 497, 498, 499, 500, 501, 502, 503, 505, 506, 507, 508, 509, 510, 511,
513, 514, 515, 516, 517, 518, 519, 521, 522, 523, 524, 525, 526, 527, 545, 546, 547, 548, 549, 550, 551, 553, 554, 555, 556, 557, 558, 559, 561, 562, 563, 564, 565, 566, 567, 569, 570, 571, 572, 573, 574, 575,
585, 586, 587, 588, 589, 590, 591, 593, 594, 595, 596, 597, 598, 599, 601, 602, 603, 604, 605, 606, 607, 641, 642, 643, 644, 645, 646, 647, 649, 650, 651, 652, 653, 654, 655, 657, 658, 659, 660, 661, 662, 663,
673, 674, 675, 676, 677, 678, 679, 681, 682, 683, 684, 685, 686, 687, 689, 690, 691, 692, 693, 694, 695, 721, 722, 723, 724, 725, 726, 727, 729, 730, 731, 732, 733, 734, 735, 737, 738, 739, 740, 741, 742, 743,
745, 746, 747, 748, 749, 750, 751, 753, 754, 755, 756, 757, 758, 759, 761, 762, 763, 764, 765, 766, 767, 769, 770, 771, 772, 773, 774, 775, 777, 778, 779, 780, 781, 782, 783, 809, 810, 811, 812, 813, 814, 815,
817, 818, 819, 820, 821, 822, 823, 825, 826, 827, 828, 829, 830, 831, 833, 834, 835, 836, 837, 838, 839, 849, 850, 851, 852, 853, 854, 855, 857, 858, 859, 860, 861, 862, 863, 865, 866, 867, 868, 869, 870, 871,
897, 898, 899, 900, 901, 902, 903, 905, 906, 907, 908, 909, 910, 911, 913, 914, 915, 916, 917, 918, 919, 921, 922, 923, 924, 925, 926, 927, 929, 930, 931, 932, 933, 934, 935, 937, 938, 939, 940, 941, 942, 943,
945, 946, 947, 948, 949, 950, 951, 953, 954, 955, 956, 957, 958, 959]
    for i in range(968):
        if i in nouse_page:
            continue
        try:
            get_all_links(i)
            time.sleep(2)
        except:
            print 'page', i, 'error'
            error_list.append(i)
            continue

    error_txt = open('error.txt', 'w')
    for i in error_list:
        error_txt.write(i)
        error_txt.write('\n')
    safari.quit()
    time.sleep(3)
    new_safari = webdriver.Safari()
    page = 'https://www.baidu.com/s?wd=%E7%94%B5%E5%BD%B1'
    new_safari = webdriver.Safari()
    new_safari.get(page)
    new_safari.maximize_window()
    error_films = []
    while len(error_list) > 0:
        deal_with_errors(error_list[0], error_films, new_safari)'''
    i = 0
    folder = os.listdir('links')
    for file in folder:
        i += 1
        if i < 40000:
            continue
        content = open(os.path.join("links", file), 'r')
        contents = content.readlines()
        page = contents[1]
        imgurl = contents[2]
        inf = [file, '', '', page, imgurl]
        q.put(inf)
        content.close()
    time.sleep(1)
    print 'q ready'
    for j in range(NUM):
        t = threading.Thread(target=no_error_contents)
        threads.append(t)
        t.setDaemon(True)
        t.start()
    for line in threads:
        line.join()