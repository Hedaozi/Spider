# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 20:11:12 2020

@author: Working
"""

#!/usr/bin/env python
# coding: utf-8

# In[import packages]:
from urllib import request
from urllib.request import urlopen
import os
import pandas
import re

# In[Functions]
def gen_url(year, index):
    url = "http://data.gtimg.cn/flashdata/hushen/daily/" + "{:0>2d}".format(year % 100) + \
          "/" + index + ".js"
    return url

def re_get_url(url, times = 0):
    try:
        response = urlopen(request.Request(url))
        text = response.read().decode('utf-8')
        return text
    except:
        if times <= 3:
            return re_get_url(url, times + 1)
        return

def decode_text(text):
    global pattern_1, pattern_2, pattern_3
    matcher = pattern_1.findall(text)
    df = pandas.DataFrame(columns = ["date", "date_stand", "opening", "closing", 
                                     "maxindex", "minindex", "deals"])
    for day in matcher:
        data = pattern_2.findall(day)
        date = data[0]; opening = data[1]; closing = data[2]
        maxindex = data[3]; minindex = data[4]
        deals = pattern_3.findall(day)[0]
        date_stand = "%s-%s-%s" % (date[0:2], date[2:4], date[4:6])
        df = df.append([{"date": date, "date_stand": date_stand, "opening": opening, 
                         "closing": closing, "maxindex": maxindex, "minindex": minindex, 
                         "deals": deals}])
    return df.reset_index(drop = True)

def get_share(index):
    share = pandas.DataFrame(columns = ["date", "date_stand", "opening", "closing", 
                                        "maxindex", "minindex", "deals"])
    for i in range(1989, 2021):
        try:
            webpage = re_get_url(gen_url(i, index))
            share = share.append(decode_text(webpage))
            print(index + " " + str(i) + " done")
        except:
            print(index + " " + str(i) + " no data")
    share.reset_index(drop = True, inplace = True)
    share.to_csv("Data/" + index + ".csv", index = False, header = True)  

def get_shares(indexs):
    if (not isinstance(indexs)):
        print("Not a list")
        return
    for index in indexs:
        get_share(index)
    return

# In[Main]
# Set workspace
os.chdir("C:/Users/Working/Desktop/Files/4-Project/market_index")

# generate pattern
p_1 = "[\d\. ]+(?=\\\\n\\\\\\n)"
pattern_1 = re.compile(p_1)
p_2 = "[\d\.]+(?= )"
pattern_2 = re.compile(p_2)
p_3 = "[\d\.]+$"
pattern_3 = re.compile(p_3)

# get shares
# get_shares(["sz399001", "sh000001"])
