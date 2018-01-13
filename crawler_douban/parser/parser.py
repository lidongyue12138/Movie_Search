# coding=utf-8
from bs4 import BeautifulSoup
from collections import defaultdict
import re
import json
import os
import time
from collections import OrderedDict

from multiprocessing import Queue, Process

# import sys
# sys.setrecursionlimit(10000)


class parser_for_movie:
    def __init__(self, receiving_queue, put_to_review_queue, \
                put_to_movie_queue, put_to_cele_queue):#之后加上put_to_movie_queue, put_to_review_queue
        self.receiving_queue = receiving_queue
        self.put_to_review_queue = put_to_review_queue
        self.put_to_movie_queue = put_to_movie_queue
        self.put_to_cele_queue = put_to_cele_queue
        while (True):
            try:
                id_num, filename = self.receiving_queue.get()
            except:
                continue

            f = open(filename, "r")
            soup = BeautifulSoup(f)
            f.close()
            tag = self.parse_tag(soup)
            try:
                genre, region, alias, director, editors, actors, time = self.parse_info(soup)
            except:
                continue
            title, year = self.parse_title(soup)
            rate = self.parse_rating(soup)
            post_href = self.parse_haibao(soup)
            plot = self.parse_plot(soup)

            try:
                celebrities = []
                for cele_name, role_name, cele_href, pic_href in self.parse_celebrities(soup):
                    if cele_name == "None":
                        continue
                    try:
                        self.saveCelebrity(cele_name, title, cele_href, role_name, pic_href)
                    except Exception as e:
                        print(e)
                        continue
                    celebrities.append(cele_name)
            except:
                celebrities = []

            self.saveMovie(title, year, rate, genre, tag, \
                        region, alias, director, editors, actors, time,post_href, plot,\
                         id_num)
            
            #put_to_review
            for href in self.parse_review(soup):
                self.put_to_review_queue.put(href)

            os.remove(filename)

    #title
    def parse_title(self, soup):
        target = soup.find("div", {"id": "content"}).h1
        title = target.find("span", {"property": "v:itemreviewed"}).get_text()
        title = title.encode("utf-8")
        try:
            year = target.find("span", {"class": "year"}).get_text()
            year = year.encode("utf-8")
            year = year.strip("(")
            year = year.strip(")")
        except:
            year = "Unknown"
        # print("%s\t%s" %(title, year))
        return title, year

    #director
    #actor
    #editor
    #genre
    #country
    #date

    def get_info(self, soup):
        info = ""
        try:
            info += soup.get_text()
            info = info.encode("utf-8")
            return info
        except:
            for i in soup.findAll("span"):
                text = get_info(i)
                text = text.encode("utf-8")
                info += "\t%s" %text
            return info

    def parse_info(self, soup):
        target = soup.find("div", {"id": "info"})
        infos = target.get_text().encode("utf-8")
        infos_dict = {}
        for line in infos.split("\n"):
            try:
                label, content = line.split(":")
                content = content.split("/")
                content = "".join(content)
                infos_dict[label] = content
            except:
                pass
        # "类型与标签": genre,
        genre = ""
        if infos_dict.has_key("类型"):
            genre = infos_dict["类型"]
        else:
            genre = "Unknown"
        genre = genre.strip()
        # "制片国家与地区": region,
        region = ""
        if infos_dict.has_key("制片国家/地区"):
            region =  infos_dict["制片国家/地区"]
        else:
            region = "Unknown"
        region = region.strip()
        # "别名": alias,
        alias = ""
        if infos_dict.has_key("又名"):
            alias = infos_dict["又名"]
        else:
            alias = "Unknown"
        alias = alias.strip()
        # "导演": director,
        director = ""
        if infos_dict.has_key("导演"):
            director = infos_dict["导演"]
        else:
            director = "Unknown"
        director = director.strip()
        # "编剧": editors,
        editors = ""
        if infos_dict.has_key("编剧"):
            editors = infos_dict["编剧"]
        else:
            editors = "Unknown"
        editors = editors.strip()
        # "演员": actors,
        actors = ""
        if infos_dict.has_key("主演"):
            actors =  infos_dict["主演"]
        else:
            actors = "Unknown"
        actors = actors.strip()
        # "时长": time
        time = ""
        if infos_dict.has_key("片长"):
            time = infos_dict["片长"]
        else:
            time = "Unknown"
        time = time.strip()
        return genre, region, alias, director, editors, actors, time


    #rating
    def parse_rating(self, soup):
        try:
            target = soup.find("div", {"class": "rating_self clearfix"})
            target = target.find("strong")
            rate = target.get_text().encode("utf-8")
            if rate == "":
                rate="0.0"
        except:
            rate = "0.0"
        # print(rate)
        rate = float(rate)
        return rate

    #plot
    def parse_plot(self, soup):
        target = soup.find("div", {"id": "link-report"})
        try:
            target = target.find("span")
            plot = target.get_text().encode("utf-8")
            plot = plot.strip()
        except:
            plot = ""
        return plot

    #comments
    def parse_comments(self, soup):
        tar_hot_comments = soup.find("div", {"id": "hot-comments"})
        for comment in tar_hot_comments.findAll("div", {"class": "comment-item"}):
            content = comment.get_text().encode("utf-8")
            content = content.strip()
            content = " ".join((content.split()))
            print(content)


    def parse_tag(self, soup):
        target = soup.find("div", {"class": "tags-body"})
        try:
            tags = target.get_text().encode("utf-8")
            tags = " ".join(tags.split("\n"))
            tags = tags.strip()
        except:
            tags = ""
        return tags

    def parse_celebrities(self, soup):
        target = soup.find("div", {"id": "celebrities"})
        if not target:
            yield ("None", "None", "None", "None")
        for celebrity in target.findAll("li", {"class": "celebrity"}):
            try:
                href = celebrity.find("a", {"title": re.compile(".*")})
            except:
                continue
            try:
                href_celebrity = href.get("href", "")
            except:
                href_celebrity = ""

            try:
                href_picture = href.find("div").get("style")
                pic_re = re.compile("(.*):url\\((.*)\\)")
                match = re.findall(r"https://.*\.jpg", href_picture)
                href_picture = match[0]
            except:
                href_picture = ""


            # print(href_celebrity)
            # print(href_picture)
            try:
                info = celebrity.find("div", {"class": "info"})
                name = info.find("a", {"class": "name"}).get("title","")
                name = name.encode("utf-8")
                try:
                    role = info.find("span", {"class": "role"}).get("title", "None")
                    role = role.encode("utf-8")
                except:
                    role = "None"
            except:
                name = "None"
                role = "None"
            # print(name)
            # print(role)

            yield (name, role, href_celebrity, href_picture)


    def saveCelebrity(self, name, movie, href, role, pic_href):
        filename = "jsonData/celebrity.json"
        # f = open(filename, 'a')
        id_num = href.split("/")[-2]
        # id_json = {"index": {"_id":id_num}}
        # json.dump(id_json, f, ensure_ascii=False)
        # f.write("\n")
        celebrity = {
                    "影人姓名": name,
                    "参演电影": movie,
                    "影人链接": href,
                    "片中角色": role,
                    "照片链接": pic_href}
        # json.dump(celebrity, f, ensure_ascii=False)
        # f.write("\n")
        # f.close()
        while True:
            if self.put_to_cele_queue.full():
                print("it's full")
                continue
            else:
                self.put_to_cele_queue.put((id_num, celebrity))
                break
        print("save one celebrity to search!")

    def saveMovie(self, name, year, rating, genre, tags,\
                    region, alias, director, editors, actors, time, post_href, plot,\
                    id_num):
        # filename = "jsonData/movie.json"
        # f = open(filename, 'a')
        movie = OrderedDict()
        movie["电影名"] = name
        movie["导演"] = director
        movie["编辑"] = editors
        movie["演员"] = actors
        movie["评分"] = rating
        movie["类型"] = genre
        movie["标签"] = tags
        movie["年份"] = year
        movie["地区"] = region
        movie["别名"] = alias
        movie["时长"] = time
        movie["海报"] = post_href
        movie["剧情"] = plot
        # movie = {
        #             "电影名": name,
        #             "参演影人": celes,
        #             "上映日期": year,
        #             "评分": rating,
        #             "类型": genre,
        #             "标签": tags,
        #             "制片国家与地区": region,
        #             "别名": alias,
        #             "导演": director,
        #             "编剧": editors,
        #             "演员": actors,
        #             "时长": time
        #             }
        # id_json = {"index": {"_id":id_num}}
        # json.dump(id_json, f, ensure_ascii=False)
        # f.write("\n")
        # json.dump(movie, f, ensure_ascii=False)
        # f.write("\n")
        # f.close()
        while True:
            if self.put_to_movie_queue.full():
                continue
            else:
                self.put_to_movie_queue.put((id_num, movie))
                break
        print("save one movie to search!")

    def parse_haibao(self, soup):
        #海报
        target = soup.find("div", {"id": "mainpic"})
        try:
            img = target.find("img")
            href = img.get("src","")
        except:
            href = ""
        return href

    def parse_review(self, soup):
        target = soup.find("div", {"class": "review-list"})
        if not target:
            return
        for review in target.findAll("div", {"class": "main-bd"}):
            h2 = review.h2
            href = h2.find("a").get("href", "")
            yield href
            # review_short = review.find("div", {"class": "review-short"}).get_text().encode("utf-8")
            # review_short = review_short.strip()
            # review_short = " ".join(review_short.split())
            # print(review_short)


def parse_review(soup):
    target = soup.find("div", {"class": "review-list"})
    if not target:
        return
    for review in target.findAll("div", {"class": "main-bd"}):
        h2 = review.h2
        href = h2.find("a").get("href", "")
        yield href
        # review_short = review.find("div", {"class": "review-short"}).get_text().encode("utf-8")
        # review_short = review_short.strip()
        # review_short = " ".join(review_short.split())
        # print(review_short)


if __name__ == '__main__':
    # q = Queue()
    # writer = Process(target=pass_data, args=(q,))
    # writer.start()
    #
    # reader = Process(target=parser_for_movie, args=(q,))
    # reader.start()
    #
    # reader.join()
    # writer.join()

    review = open("review.txt", "w")
    counter = 0
    for filename in os.listdir("html"):
            filename = os.path.join("html", filename)
            f = open(filename, "r")
            soup = BeautifulSoup(f)
            for href in parse_review(soup):
                review.write(href)
                review.write("\n")
    review.close()
