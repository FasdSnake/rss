#!/usr/bin/python3
# coding=utf-8

import os, sys, time, datetime, smtplib
import urllib.request
import xml.etree.ElementTree as ET

TFORM = '%a, %d %b %Y %H:%M:%S GMT'

def parseItem(item):
    result = {}
    for k in item.getchildren():
        result[k.tag] = k.text
    return result['guid'], result

try:
    data = set(os.listdir('data'))
except FileNotFoundError:
    os.mkdir('data')
    data = set()

def sendmail(title, body):
    with open('login.txt') as f:
        args = eval(f.read())
    if 'notinited' in args:
        print('Please edit login.txt first.', file = sys.stderr)
        exit(1)
    if type(title) is not str:
        title = title.decode()
    if type(body) is not str:
        body = body.decode()
    for to in args['tos']:
        p = os.popen('mail -a "Content-Type: text/plain; charset=utf-8;" -s "'+title+'" '+to, 'w')
        p.write(body)
        p.close()

def show(guid, detail):
    result = ''
    if 'title' in detail:
        result += detail['title'] + '\n'
    if 'link' in detail:
        result += detail['link'] + '\n\n'
    else:
        result += guid + '\n\n'
    if 'description' in detail:
        result += detail['description'] + '\n'
    #result += '\n'
    '''
    for key in detail:
        if key in ('title', 'link', 'guid', 'description'):
            continue
        if detail[key]:
            result += key + ': ' + detail[key] + '\n\n'
    '''
    return result

with open('list.txt') as f:
    os.chdir('data')
    rsss = list(map(str.strip, f.readlines()))
    count = len(rsss)
    for i in range(count):
        rss = rsss[i]
        name, _, url = rss.partition(': ')
        print('[%3d/%3d] %s' % (i+1, count, name), file = sys.stderr, flush = True)

        # get the last info
        if name in data:
            with open(name) as df:
                lastmodi, last = eval(df.read())
        else:
            lastmodi, last = 0, set()

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
                        last.add(guid)
                        sendmail('RSS <%s>: new post' % name, show(guid, detail))
        except Exception as e:
            print('fail to fetch <%s>: %s' % (name, str(e)), file = sys.stderr, flush = True)
            continue

        # write to the file
        with open(name, 'w') as df:
            df.write(repr((newmodi, last)))
