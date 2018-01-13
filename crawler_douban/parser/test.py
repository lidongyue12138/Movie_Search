# coding=utf-8
import sys
from bs4 import BeautifulSoup
from collections import defaultdict
import re
import json
import os
import time
from collections import OrderedDict

from multiprocessing import Queue, Process

#plot
def parse_plot(soup):
    target = soup.find("div", {"id": "link-report"})
    target = target.find("span")
    plot = target.get_text().encode("utf-8")
    plot = plot.strip()
    print(plot)

for filename in os.listdir("movies"):
    f = open(os.path.join("movies", filename), "r")
    soup = BeautifulSoup(f)
    parse_plot(soup)
