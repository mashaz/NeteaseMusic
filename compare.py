# -*- coding:utf-8 -*-
#!/usr/bin/env python

__auther__ = 'xiaohuahu94@gmail.com'

'''
如何获取js实现的内容
todos:
抓取用户
top100比较
'''

import requests
from bs4 import BeautifulSoup
import re
import os
import sys
import time
import random
import json
import sqlite3
from collections import Counter


reload(sys)
sys.setdefaultencoding('utf-8')   # note
requests.adapters.DEFAULT_RETRIES = 5 

STYLE = {
        'fore':
        {   # 前景色
            'black'    : 30,   #  黑色
            'red'      : 31,   #  红色
            'green'    : 32,   #  绿色
            'yellow'   : 33,   #  黄色
            'blue'     : 34,   #  蓝色
            'purple'   : 35,   #  紫红色
            'cyan'     : 36,   #  青蓝色
            'white'    : 37,   #  白色
        },

        'back' :
        {   # 背景
            'black'     : 40,  #  黑色
            'red'       : 41,  #  红色
            'green'     : 42,  #  绿色
            'yellow'    : 43,  #  黄色
            'blue'      : 44,  #  蓝色
            'purple'    : 45,  #  紫红色
            'cyan'      : 46,  #  青蓝色
            'white'     : 47,  #  白色
        },

        'mode' :
        {   # 显示模式
            'mormal'    : 0,   #  终端默认设置
            'bold'      : 1,   #  高亮显示
            'underline' : 4,   #  使用下划线
            'blink'     : 5,   #  闪烁
            'invert'    : 7,   #  反白显示
            'hide'      : 8,   #  不可见
        },

        'default' :
        {
            'end' : 0,
        },
}


def UseStyle(string, mode = '', fore = '', back = ''):

    mode  = '%s' % STYLE['mode'][mode] if STYLE['mode'].has_key(mode) else ''

    fore  = '%s' % STYLE['fore'][fore] if STYLE['fore'].has_key(fore) else ''

    back  = '%s' % STYLE['back'][back] if STYLE['back'].has_key(back) else ''

    style = ';'.join([s for s in [mode, fore, back] if s])

    style = '\033[%sm' % style if style else ''

    end   = '\033[%sm' % STYLE['default']['end'] if style else ''

    return '%s%s%s' % (style, string, end)


def GetCookies():  

	f = open('cookies.txt','r')
	cookies = {}
	for line in f.read().split(';'):
		name,value = line.strip().split('=',1)
		cookies[name] = value
	return cookies

def GetTopAllTime(uid):

    url = 'http://music.163.com/user/songs/rank?id='+str(uid)
    cookies = GetCookies()
    headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
                ,'Referer':'http://music.163.com'
                ,'Host':'music.163.com'
                ,'Accept':'*/*'}
    respo = requests.get(url,headers=headers,cookies=cookies)
    soup = BeautifulSoup(respo.content)
    print soup
    

def GetTopLastWk():
    pass


def GetPlayListDetail(plid):

    songList = []
    singerList = []
    url = 'http://music.163.com/playlist?id='+str(plid)
    headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}
    respo = requests.get(url,headers=headers)
    soup = BeautifulSoup(respo.content)
    main = soup.find('ul',{'class':'f-hide'})

    for music in main.findAll('a'):
        songList.append(music.text)
        #print music.text

    singermain  = soup.find('textarea',{'style':'display:none;'})
    xxx = str(singermain.contents[0]).lstrip("u'").rstrip("'")
    try:
        d = json.loads(xxx)
        for i in range(0,len(d)):
            singerList.append(d[i]['artists'][0]['name'])
    except:
        for i in range(0,len(songList)):
            singerList.append("unknown")
    

    return songList,singerList
  

    #print data.artists

def GetAllListId(uid):

    url = 'http://music.163.com/user/home?id='+str(uid)
    respo = requests.get(url)
    re_count = re.compile(r'cCount:[0-9]{1,3},')
    ccount = int(re.findall(re_count,respo.content)[0].lstrip('cCount:').rstrip(',')) #创建的歌单数

    offset=0
    limit=100
    url = 'http://music.163.com/api/user/playlist/?offset={}&limit={}&uid={}'.format(offset,limit,uid)
    '''
    为csrf_token搞了大半天，感谢github上的musicbox项目,上了api,早该直接看api,次数太少被ban
    '''
    respo = requests.get(url)
    print '获得歌单list,解析中...'
    re_id = re.compile(r'\"id\":[0-9]{6,9}\D')
    #re_name = re.compile(r'\"name\":[a-zA-Z0-9]{1,50}\"')  把歌单名取出来json
    idlist = re.findall(re_id,respo.content)
    #namelist = re.findall(re_name,respo.content)
    for i in range(0,len(idlist)):
        idlist[i] = idlist[i].lstrip('"id":').rstrip('}').rstrip(',')
    idlist = idlist[0:ccount]
    print '解析完毕'
    return  idlist   #创建的所有的歌单id列表

def singerAnalysis(singerList,flag):

    word_counts = Counter(singerList)
    top_three = word_counts.most_common(3)
    try:
        x1 = top_three.pop()
        x2 = top_three.pop()
        x3 = top_three.pop()
        print UseStyle('收藏第三多的歌手:%s(%s次)'%(x1[0],x1[1]),fore="white")
        print UseStyle('收藏第二多的歌手:%s(%s次)'%(x2[0],x2[1]),fore="blue")
        print UseStyle('收藏最多的歌手:%s(%s次)'%(x3[0],x3[1]),fore="purple")
    except:
            print '看来你收藏的不够多哦！'

def compare(ilist_id,ulist_id):
    iLikeSongList,iSingerList = GetPlayListDetail(ilist_id) #playlist id not user id
    time.sleep(1)
    uLikeSongList,uSingerList = GetPlayListDetail(ulist_id)
    for i in range(0,len(iLikeSongList)):
        iLikeSongList[i] = iLikeSongList[i] + ' - ' + iSingerList[i]
    for i in range(0,len(uLikeSongList)):
        uLikeSongList[i] = uLikeSongList[i] + ' - ' + uSingerList[i]
    print '你'
    singerAnalysis(iSingerList,0)
    print 'Ta'
    singerAnalysis(uSingerList,0)
    print UseStyle('你喜欢的音乐列表有%d首歌'%(len(iLikeSongList)),fore='cyan') 
    time.sleep(1)
    print UseStyle('Ta喜欢的音乐列表有%d首歌'%(len(uLikeSongList)),fore='cyan') 
    time.sleep(1)
    sameSongList = []
    for isong in iLikeSongList:
        for usong in uLikeSongList:
            if str(isong) == str(usong):
                sameSongList.append(isong)
    sameSongList = list(set(sameSongList))
    if len(sameSongList) == 0:
        print UseStyle('Oooops,没有任何交集',fore='red') 
    else:
        print UseStyle('你们有%d首共同喜欢的歌'%(len(sameSongList)),fore='red') 
    for song in sameSongList:
        print song

def CompareAll(iplaylist,uplaylist):
    allMyPlayList = []
    allMySingerList = []
    allYouPlayList = []
    allYouSingerList = []
    print '获得歌单中',
    for playlist in iplaylist:
        print '.',
        iLikeSongList , iSingerList = GetPlayListDetail(playlist)
        time.sleep(1)
        allMyPlayList.extend(iLikeSongList)
        allMySingerList.extend(iSingerList)
    #print len(allMyPlayList)
    for playlist in uplaylist:
        print '.',
        uLikeSongList , uSingerList = GetPlayListDetail(playlist)
        time.sleep(1)
        allYouPlayList.extend(uLikeSongList)
        allYouSingerList.extend(uSingerList)
    print
    for i in range(0,len(allMyPlayList)):
        allMyPlayList[i] = allMyPlayList[i] + ' - ' + allMySingerList[i]
    for i in range(0,len(allYouPlayList)):
        allYouPlayList[i] = allYouPlayList[i] + ' - ' + allYouSingerList[i]
    print '你'
    singerAnalysis(allMySingerList,1)
    print 'Ta'
    singerAnalysis(allYouSingerList,1)
    print UseStyle('你的所有音乐列表有%d首歌'%(len(allMyPlayList)),fore='cyan') 
    time.sleep(1)
    print UseStyle('Ta的所有音乐列表有%d首歌'%(len(allYouPlayList)),fore='cyan') 
    time.sleep(1)
    sameSongList = []
    for isong in allMyPlayList:
        for usong in allYouPlayList:
            if str(isong) == str(usong):
                sameSongList.append(isong)
    sameSongList = list(set(sameSongList))
    if len(sameSongList) == 0:
        print UseStyle('Oooops,没有任何交集',fore='red') 
    else:
        print UseStyle('你们有%d首共同喜欢的歌'%(len(sameSongList)),fore='red') 
    for song in sameSongList:
        print song


def UserSearch(username):

    url = 'http://music.163.com/api/search/get?s='+str(username)+'&type=1002&offset=0&limit=60'
    respo = requests.post(url)
    return  respo.content

def main():
    if not os.path.exists('info.txt'):
        os.system('touch info.txt')
    if len(sys.argv) == 1:#对比我喜欢的
            ilikedplaylist = GetAllListId('41977865')[0]
            ulikedplaylist = GetAllListId('100953635')[0]
            compare(ilikedplaylist,ulikedplaylist)
    else:
        if sys.argv[1].startswith('--'):     
            option = sys.argv[1][2:]     
            if (option == 'help'):
                print '****************碰撞一下彼此的歌单****************'
                print 
                print '*******************操作指南*********************'
                print 
                print UseStyle('1. python compare.py',fore='cyan')
                print 
                print UseStyle('2. python compare.py -a',fore='cyan')
                print  
        elif sys.argv[1].startswith('-'): 
                option = sys.argv[1][1:] 
                if(option == 'a'):#对比所有歌单
                    iplaylist = GetAllListId('41977865')
                    uplaylist = GetAllListId('273681273')
                    CompareAll(iplaylist,uplaylist)
                elif (option == 'i'):
                    print '你的昵称:'
                    myname = raw_input()
                    
                    nameJson = UserSearch(myname)
                    d = json.loads(nameJson)
                    myname = d['result']['userprofiles'][0]['nickname']
                    myid = d['result']['userprofiles'][0]['userId']
                    print '你的用户名和ID是否为%s,%s:任意键继续,Q退出'%(myname,myid)
                    wait = raw_input()
                    if wait=='q' or wait == 'Q' :
                        exit()
                    iplaylist = GetAllListId(myid)[0]

                    print '对方昵称:'
                    uname = raw_input()

                    nameJson = UserSearch(uname)
                    d = json.loads(nameJson)
                    uname = d['result']['userprofiles'][0]['nickname']
                    uid = d['result']['userprofiles'][0]['userId']
                    print '你的用户名和ID是否为%s,%s:任意键继续,Q退出'%(uname,uid)
                    wait = raw_input()
                    if wait=='q' or wait == 'Q' :
                        exit()
                    uplaylist = GetAllListId(uid)[0]
                    compare(iplaylist,uplaylist)
                elif (option == 'ai' or option == "ia"):
                    print '你的昵称:'
                    myname = raw_input()
                    nameJson = UserSearch(myname)
                    d = json.loads(nameJson)
                    myname = d['result']['userprofiles'][0]['nickname']
                    myid = d['result']['userprofiles'][0]['userId']
                    print '你的用户名和ID是否为%s,%s:任意键继续,Q退出'%(myname,myid)
                    wait = raw_input()
                    if wait=='q' or wait == 'Q' :
                        exit()
                    iplaylist = GetAllListId(myid)

                    print '对方昵称:'
                    uname = raw_input()

                    nameJson = UserSearch(uname)
                    d = json.loads(nameJson)
                    uname = d['result']['userprofiles'][0]['nickname']
                    uid = d['result']['userprofiles'][0]['userId']
                    print '你的用户名和ID是否为%s,%s:任意键继续,Q退出'%(uname,uid)
                    wait = raw_input()
                    if wait=='q' or wait == 'Q' :
                        exit()
                    uplaylist = GetAllListId(uid)
                    CompareAll(iplaylist,uplaylist)
    
    #根据uid递增,查找,sleep,需要时间
    #把简单的数据本地化 防止api次数 先本地化喜欢的歌曲
    #todo
    
if __name__ == '__main__':
    main()
    #GetPlayListDetail('483486909')


