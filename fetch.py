#!/usr/bin/python3
# coding=utf-8

import os, time, datetime
import urllib.request
import xml.etree.ElementTree as ET

TFORM = '%a, %d %b %Y %H:%M:%S GMT'

def parseItem(item):
    result = dict()
    for k in item.getchildren():
        result[k.tag] = k.text
    return result['guid'], result

try:
    data = set(os.listdir('data'))
except FileNotFoundError:
    os.mkdir('data')
    data = set()

with open('list.txt') as f:
    os.chdir('data')
    rsss = list(map(str.strip, f.readlines()))
    count = len(rsss)
    for i in range(count):
        rss = rsss[i]
        name, _, url = rss.partition(': ')
        print('[%3d/%3d] %s' % (i+1, count, name))

        # get the last info
        if name in data:
            with open(name) as df:
                lastmodi, last = eval(df.read())
        else:
            lastmodi, last = 0, dict()

        # fetch the new info
        changed = False
        try:
            with urllib.request.urlopen(url) as http:
                t = http.getheader('Last-Modified')
                if t:
                    t = time.strptime(http.getheader('Last-Modified'), TFORM)
                    newmodi = datetime.datetime(t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec, tzinfo=datetime.timezone.utc).timestamp()
                    if newmodi == lastmodi:
                        continue
                else:
                    newmodi = 0
                for item in ET.parse(http).iterfind('./channel/item'):
                    guid, detail = parseItem(item)
                    if guid not in last:
                        changed = True
                        last[guid] = detail
                        print(name + ': ' + guid)
        except Exception as e:
            print('fail to fetch <%s>: %s' % (name, str(e)))
            continue

        # write to the file
        with open(name, 'w') as df:
            df.write(repr((newmodi, last)))
