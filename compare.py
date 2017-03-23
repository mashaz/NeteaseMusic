# -*- coding:utf-8 -*-
#!/usr/bin/env python

__auther__ = 'xiaohuahu94@gmail.com'

'''
todo
在所有歌单对比中加入用户top100的对比
'''

import requests
import re
import os
import sys
import time
import random
import json
import gb2260
from bs4 import BeautifulSoup
from collections import Counter
from selenium import webdriver
from selenium.webdriver.common.by import By

global wname
global tname

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
'''带Style输出'''
def UseStyle(string, mode = '', fore = '', back = ''):

    mode  = '%s' % STYLE['mode'][mode] if STYLE['mode'].has_key(mode) else ''
    fore  = '%s' % STYLE['fore'][fore] if STYLE['fore'].has_key(fore) else ''
    back  = '%s' % STYLE['back'][back] if STYLE['back'].has_key(back) else ''
    style = ';'.join([s for s in [mode, fore, back] if s])
    style = '\033[%sm' % style if style else ''
    end   = '\033[%sm' % STYLE['default']['end'] if style else ''
    return '%s%s%s' % (style, string, end)


class People:
    def __init__(self,username,uid,gender,birthday,province,city):
        self.username = username
        self.uid = uid
        self.gender = gender
        self.birthday = birthday
        self.province = province
        self.city = city
        self.datetime = str(time.strftime('%Y-%m-%d',time.localtime(time.time())))
        #people = People(myname,myid,gender,birthday,province,city)
        
def GetCookies():  

	f = open('cookies.txt','r')
	cookies = {}
	for line in f.read().split(';'):
		name,value = line.strip().split('=',1)
		cookies[name] = value
	return cookies

'''获得所有时间听歌次数Top100'''
def GetTopAllTime(uid):  
    songNameList = []
    singerList = []
    url = 'http://music.163.com/user/songs/rank?id=' + str(uid)
    browser = webdriver.PhantomJS(executable_path='/Users/Mashaz/phantomjs-2.1.1-macosx/bin/phantomjs')
    #browser = webdriver.Chrome(executable_path='/Users/Mashaz/chromedriver')
    
    try:
        browser.get(url)
        browser.implicitly_wait(30)
        browser.switch_to_frame('g_iframe')
        browser.find_element_by_id('songsall').click()
        browser.implicitly_wait(30)
        time.sleep(3)   #  !!!
    
        soup = BeautifulSoup(browser.page_source)
        page_content = soup.findAll('div',attrs={'id','m-record'})[0]   #weekly top100歌单div
        soupSingerList = soup.findAll('div',attrs={'class','ttc'})
        for i in range(0,len(soupSingerList)):
            singerList.append(soupSingerList[i].contents[0].contents[1].contents[2].contents[0].contents[0])

        songslist = soup.findAll('b')

        for i in range(0,len(songslist)):
            songNameList.append(songslist[i].contents[0]+' - '+singerList[i])
        browser.close()
        return songNameList
    except:
        browser.close()
        return []    

'''获得上周Top100'''
def GetTopLastWk(uid):
    songNameList = []
    singerList = []
    url = 'http://music.163.com/user/songs/rank?id=' + str(uid)
    browser = webdriver.PhantomJS(executable_path='/Users/Mashaz/phantomjs-2.1.1-macosx/bin/phantomjs')
    #browser = webdriver.Chrome(executable_path='/Users/Mashaz/chromedriver')


    try:
        browser.get(url)
        browser.implicitly_wait(30)
        time.sleep(3)
        browser.switch_to_frame('g_iframe')
        soup = BeautifulSoup(browser.page_source)
        page_content = soup.findAll('div',attrs={'id','m-record'})[0]   #weekly top100歌单div
    
        soupSingerList = soup.findAll('div',attrs={'class','ttc'})
        for i in range(0,len(soupSingerList)):
            singerList.append(soupSingerList[i].contents[0].contents[1].contents[2].contents[0].contents[0])
    
        songslist = soup.findAll('b')
    
        no = 1
        for i in range(0,len(songslist)):
            songNameList.append(songslist[i].contents[0]+' - '+singerList[i])
        browser.close()
        return songNameList
    except:
        #print 'Ooooops,该用户隐藏了该动态'
        browser.close()
        return []

def CompareTopWeekly(mylist,ulist):
    if mylist!=[] and ulist!=[]:
        print wname,
        print '******************'
        print tname
        for i in range(0,10):
            print '*******************听歌排行-上周最多********************'
            print i,
            print mylist[i],
            print ':',
            print ulist[i]
    else:
        print 'Ooooops'

def CompareTopAllTime(mylist,ulist):
    if mylist!=[] and ulist!=[]:
        print wname,
        print '******************'
        print tname
        for i in range(0,10):
            print '*******************听歌排行-所有时间********************'
            print i,
            print mylist[i],
            print ':',
            print ulist[i]

    else:
        print 'Ooooops'

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
    为csrf_token搞了大半天，感谢github上的musicbox项目,上了api,但api次数太少会被ban
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
        print UseStyle('收藏最多的歌手:%s(%s次)'%(x3[0],x3[1]),fore="purple")
        print UseStyle('收藏第二多的歌手:%s(%s次)'%(x2[0],x2[1]),fore="blue")
        print UseStyle('收藏第三多的歌手:%s(%s次)'%(x1[0],x1[1]),fore="white")
    except:
        print '看来你收藏的不够多哦！'
def SingleListAnlyasis(people):

    print '爬取所有时间Top100中...'
    myAllList = GetTopAllTime(people.uid)
    time.sleep(2)
    print '爬取完毕'
    print '爬取上周Top100中...'
    myWeekList = GetTopLastWk(people.uid)
    print '爬取完毕'
    if myAllList == []:
        print 'Ooooops,该用户隐藏了动态'
    else :
               
        myAllSongList = []
        myAllSingerList = []
        for song in myAllList:
            s = song.split('-')
            myAllSongList.append(s[0].strip())
            myAllSingerList.append(s[1].strip())
        print UseStyle('所有时间Top10' ,fore= 'cyan' )  #自行修改输出数
        if len(myAllList)>9:
            for i in range(0,10):
                print myAllList[i]
        print UseStyle('上周Top10'   ,fore = 'cyan') 
        try:
            for i in range(0,10):
                print myWeekList[i]
        except:
            for song in myWeekList:
                print song
        print UseStyle('----------------所有时间Top100分析结果-----------------'  ,fore = "cyan")

        singers_counts = Counter(myAllSingerList)
        top_three = singers_counts.most_common(3)
        try:
            x1 = top_three.pop()
            x2 = top_three.pop()
            x3 = top_three.pop()
            print UseStyle('Top100听的最多的歌手:%s(%s次)'%(x3[0],x3[1]),fore="purple")
            print UseStyle('Top100听的第二多的歌手:%s(%s次)'%(x2[0],x2[1]),fore="blue")
            print UseStyle('Top100听的第三多的歌手:%s(%s次)'%(x1[0],x1[1]),fore="white")
        except:
            print '看来你听的不够多哦！'
    if myWeekList == []:
        print 'Ta上周没有听歌哦'
    else:
        myWeekSongList = []
        myWeekSingerList = []
        for song in myWeekList:
            s = song.split('-')
            myWeekSongList.append(s[0].strip())
            myWeekSingerList.append(s[1].strip())

        print UseStyle('----------------上周Top100分析结果-----------------'  ,fore = "cyan")

        singers_counts = Counter(myWeekSingerList)
        top_three = singers_counts.most_common(3)
        try:
            x1 = top_three.pop()
            x2 = top_three.pop()
            x3 = top_three.pop()
            print UseStyle('上周Top100听的最多的歌手:%s(%s次)'%(x3[0],x3[1]),fore="purple")
            print UseStyle('上周Top100听的第二多的歌手:%s(%s次)'%(x2[0],x2[1]),fore="blue")
            print UseStyle('上周Top100听的第三多的歌手:%s(%s次)'%(x1[0],x1[1]),fore="white")
        except:
            print '看来你上周听的不够多哦！'
    # print '输入X(X为1-100内的数字)+Enter输出详细TopX榜单,直接Enter退出'
    # flag_print_detail = raw_input()       
    # if flag_print_detail <  101 and flag_print_detail > 0 :
    #     if(flag_print_detail<len(myAllList)):
    #         print '听歌不够多。。。'
    #     else :
    #         for i in range(0,flag_print_detail):
    #             print myAllList[i],
    #             print '     '
    #             print myWeekList[i]
    # else :
    #     print '退出'
    #     exit()

def compare(ilist_id,ulist_id):
    iLikeSongList,iSingerList = GetPlayListDetail(ilist_id) #playlist id not user id
    time.sleep(1)
    uLikeSongList,uSingerList = GetPlayListDetail(ulist_id)
    for i in range(0,len(iLikeSongList)):
        iLikeSongList[i] = iLikeSongList[i] + ' - ' + iSingerList[i]
    for i in range(0,len(uLikeSongList)):
        uLikeSongList[i] = uLikeSongList[i] + ' - ' + uSingerList[i]
    global wname,tname
    print '------------------------------------------------------'
    print UseStyle(wname,back='blue')
    singerAnalysis(iSingerList,0)
    print '------------------------------------------------------'
    print UseStyle(tname,back='blue')
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

    global wname,tname
    print '------------------------------------------------------'
    print UseStyle(wname,back='blue')
    singerAnalysis(allMySingerList,1)
    print '------------------------------------------------------'
    print UseStyle(tname,back='blue')
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
    return  respo.content  #json

def UsernameInput():
    try:
        print '你的昵称:'
        myname = raw_input()
        nameJson = UserSearch(myname)
        d = json.loads(nameJson)
        try:
            myname = d['result']['userprofiles'][0]['nickname']
        except:
            print '查无此人'
        myid = d['result']['userprofiles'][0]['userId']
        gender = d['result']['userprofiles'][0]['gender']
        birthday = d['result']['userprofiles'][0]['birthday']
        city = d['result']['userprofiles'][0]['city']
        province = d['result']['userprofiles'][0]['province']
        if birthday < 0 :
            birthday = 'unknown'
        else:
            x = time.localtime(float(birthday/1000))
            birthday = time.strftime('%Y-%m-%d',x)
        try:
            province = gb2260.get(province).name
        except:
            province = 'unknown'
        try:
            city = gb2260.get(city).name
        except:
            city = 'unknown'
        if gender == 1 :
            gender = 'male'
        elif gender == 2:
            gender = 'female'
        else :
            gender = 'unknown'
        print '你的用户名和ID是否为%s,%s:任意键继续,Q退出'%(myname,myid)
        wait = raw_input()
        if wait=='q' or wait == 'Q' :
            exit()
        peopleMe  = People(myname,myid,gender,birthday,province,city)
        print '对方昵称:'
        uname = raw_input()
        nameJson = UserSearch(uname)
        d = json.loads(nameJson)
        try:
            uname = d['result']['userprofiles'][0]['nickname']
        except:
            print '查无此人'
        uid = d['result']['userprofiles'][0]['userId']
        gender = d['result']['userprofiles'][0]['gender']
        birthday = d['result']['userprofiles'][0]['birthday']
        city = d['result']['userprofiles'][0]['city']
        province = d['result']['userprofiles'][0]['province']
        if birthday < 0 :
            birthday = 'unknown'
        else:
            x = time.localtime(float(birthday/1000))
            birthday = time.strftime('%Y-%m-%d',x)
        try:
            province = gb2260.get(province).name
        except:
            province = 'unknown'
        try:
            city = gb2260.get(city).name
        except:
            city = 'unknown'
        if gender == 1 :
            gender = 'male'
        elif gender == 2:
            gender = 'female'
        else :
            gender = 'unknown'

        print '你的用户名和ID是否为%s,%s:任意键继续,Q退出'%(uname,uid)
        wait = raw_input()
        if wait=='q' or wait == 'Q' :
            exit()
        peopleU  = People(uname,uid,gender,birthday,province,city)
        global wname
        global tname
        wname = myname
        tname = uname
        return peopleMe.uid,peopleU.uid
    except Exception ,e :
        print str(e)
        print '不存在这个用户名'
        exit()

def GetSomeUsers(songid):
    songNameList = []
    singerList = []
    url = 'http://music.163.com/song?id=' + str(songid)
    browser = webdriver.PhantomJS(executable_path='/Users/Mashaz/phantomjs-2.1.1-macosx/bin/phantomjs')
    #browser = webdriver.Chrome(executable_path='/Users/Mashaz/chromedriver')
    browser.get(url)
    browser.implicitly_wait(30)
    browser.switch_to_frame('g_iframe')
    #browser.find_element_by_xpath('//span[@id="songsall"]').click()
    #browser.find_element_by_id('songsall').click()
    time.sleep(3)   #  !!!
    
    soup = BeautifulSoup(browser.page_source)
    try:
        page_content = soup.findAll('a',attrs={'class','s-fc7'})   #weekly top100歌单div
        
        userlist = []
        for item in range(0,20):
            x = page_content.pop().contents[0]
            userlist.append(x)
        userlist = list(set(userlist))
        sfile = open('user.txt','a')
        for user in userlist:
            sfile.write(user)
            sfile.write('\n')
        sfile.close()
    except:
        return []    
def main():

    if len(sys.argv) == 1:#对比我喜欢的
            print UseStyle('***单用户top100分析***',fore = 'red')
            print '输入你的昵称:'
            myname = raw_input()
            nameJson = UserSearch(myname)
            d = json.loads(nameJson)
            try:
                myname = d['result']['userprofiles'][0]['nickname']
            except:
                print '查无此人'
            myid = d['result']['userprofiles'][0]['userId']
            gender = d['result']['userprofiles'][0]['gender']
            birthday = d['result']['userprofiles'][0]['birthday']
            city = d['result']['userprofiles'][0]['city']
            province = d['result']['userprofiles'][0]['province']
            if birthday < 0 :
                birthday = 'unknown'
            else:
                x = time.localtime(float(birthday/1000))
                birthday = time.strftime('%Y-%m-%d',x)
            try:
                province = gb2260.get(province).name
            except:
                province = 'unknown'
            try:
                city = gb2260.get(city).name
            except:
                city = 'unknown'
            if gender == 1 :
                gender = 'male'
            elif gender == 2:
                gender = 'female'
            else :
                gender = 'unknown'
            people = People(myname,myid,gender,birthday,province,city)
            print '你的用户名和ID是否为%s,%s:任意键继续,Q退出'%(myname,myid)
            wait = raw_input()
            if wait=='q' or wait == 'Q' :
                exit()
            print '开始分析...'
            SingleListAnlyasis(people)

    else:
        if sys.argv[1].startswith('--'):     
            option = sys.argv[1][2:]     
            if (option == 'help'):
                print 
                print '****************碰撞一下彼此的歌单****************'
                print 
                print '*******************操作指南*********************'
                print 
                print UseStyle('1. python compare.py',fore='cyan')
                print 
                print UseStyle('3. python compare.py -i #i for input your name' ,fore='cyan')
                print  
                print UseStyle('4. python compare.py -ai #a for all songlist',fore='cyan')
                print  
                print UseStyle('5. python compare.py -ti #t for top' ,fore='cyan')
                print  

        elif sys.argv[1].startswith('-'): 
                option = sys.argv[1][1:] 
                if(option == 'g'):
                    pass
                elif (option == 'i'):

                    myid , uid = UsernameInput()

                    iplaylist = GetAllListId(myid)[0]
                    uplaylist = GetAllListId(uid)[0]

                    compare(iplaylist,uplaylist)
                elif (option == 'ai' or option == "ia"):
                
                    
                    myid,uid = UsernameInput()

                    iplaylist = GetAllListId(myid)
                    uplaylist = GetAllListId(uid)
                
                    CompareAll(iplaylist,uplaylist)
                elif (option == 'ti' or option == "it"):
                    
                    myid , uid  = UsernameInput()

                    myWeekList = GetTopLastWk(myid)
                    myAllList = GetTopAllTime(myid)
                    uWeekList = GetTopLastWk(uid)
                    uAllList = GetTopAllTime(uid)

                    CompareTopWeekly(myWeekList,uWeekList)
                    CompareTopAllTime(myAllList,uAllList)


if __name__ == '__main__':
    main()
    


