# -*- coding: gbk -*-
'''
Copyright (c) 2014 lsich.com 罗思成
'''
import time
import getpass
import urllib2
import urllib
import cookielib
from sgmllib import SGMLParser
 
class ListName(SGMLParser):
	def __init__(self):
	    SGMLParser.__init__(self)
            self.is_a = ''
            self.name = []
	def start_a(self, attrs):
            for name, value in attrs:
                if (name == 'href' and value == 'javascript:void(0)'):
                    self.is_a = 1
                    return
	def end_a(self):
	    self.is_a = ''
	def handle_data(self, text):
	    if self.is_a == 1:
		self.name.append(text)
		
def show(content, courseType, wanted):
    content = content[content.find('可选课程'):]
    listname = ListName()
    listname.feed(content)
    print courseType+'个数', len(listname.name)
    for item in listname.name:
        print item
    if ((wanted == courseType or wanted == '全部') and len(listname.name) > 0):
        print '\a'*2


def login(user):
    try:
        # 设置
        cookie = cookielib.CookieJar()
        cookieProc = urllib2.HTTPCookieProcessor(cookie)
        opener = urllib2.build_opener(cookieProc)
        urllib2.install_opener(opener)

        # 请求
        header1 = {  'Host'            : 'uems.sysu.edu.cn',
                     'Connection'      : 'keep-alive',
                     'Content-Length'  : '68',
                     'Cache-Control'   : 'max-age=0',
                     'Accept'          : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                     'Origin'          : 'http://uems.sysu.edu.cn',
                     'Content-Type'    : 'application/x-www-form-urlencoded',
                     'Referer'         : 'http//uems.sysu.edu.cn/elect/',
                     'Accept-Encoding' : 'gzip,deflate,sdch',
                     'Accept-Language' : 'zh-CN,zh;q=0.8',
                     'User-Agent'      : 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) \
                                        Chrome/35.0.1916.153 Safari/537.36',
                  }
        
        user = urllib.urlencode(user)
        req = urllib2.Request(
                    url = 'http://uems.sysu.edu.cn/elect/login',
                    data = user,
                    headers = header1
                )
        res = urllib2.urlopen(req)
        sid = res.geturl().replace('http://uems.sysu.edu.cn/elect/s/types?sid=', '')
        return sid
    except urllib2.HTTPError, e:
        print 'error', e.code
        return 0
        
def course(sid, wanted):
    try:
        #请求
        header =  {  'Host'            : 'uems.sysu.edu.cn',
                     'Connection'      : 'keep-alive',
                     'Accept'          : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                     'Referer'         : 'http://uems.sysu.edu.cn/elect/s/types?sid='+sid,
                     'Accept-Encoding' : 'gzip,deflate,sdch',
                     'Accept-Language' : 'zh-CN,zh;q=0.8',
                     'User-Agent'      : 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) \
                                          Chrome/35.0.1916.153 Safari/537.36',
                  }
        
        # 专选
        req = urllib2.Request(
                    url = 'http://uems.sysu.edu.cn/elect/s/courses?kclb=21&xnd=2014-2015&xq=1&xqm=4&blank=1&sid='+sid,
                    #kclb=30&xqm=4&sort=&ord=&xnd=2014-2015&xq=1&sid=ec1c7f88-e90c-4f18-9bf1-efc4d5223178
                    headers = header
                )
        res = urllib2.urlopen(req)
        content = res.read().decode('utf-8').encode('gb2312')
        show(content, '专选', wanted)

        # 公选
        req = urllib2.Request(
                    url = 'http://uems.sysu.edu.cn/elect/s/courses?kclb=30&xnd=2014-2015&xq=1&xqm=4&blank=1&sid='+sid,
                    headers = header
                )
        res = urllib2.urlopen(req)
        content = res.read().decode('utf-8').encode('gb2312')
        show(content, '公选', wanted)
        
        '''
        # 专必
        req = urllib2.Request(
                    url = 'http://uems.sysu.edu.cn/elect/s/courses?kclb=11&xnd=2014-2015&xq=1&sid='+sid,
                    headers = header
                )
        res = urllib2.urlopen(req)
        content = res.read().decode('utf-8').encode('gb2312')
        show(content, '专必', wanted)
            
        
            
        # 公必
        req = urllib2.Request(
                    url = 'http://uems.sysu.edu.cn/elect/s/courses?kclb=10&xnd=2014-2015&xq=1&sid='+sid,
                    headers = header
                )
        res = urllib2.urlopen(req)
        content = res.read().decode('utf-8').encode('gb2312')
        show(content, '公必', wanted)
        '''
        return sid
    except urllib2.HTTPError, e:
        # print 'error', e.reason, e.code
        return 0
        
def init():
    print '---------------设置参数---------------'
    print '----当你关注的课程有多余时会响一声----'
    print '----------刷新间隔默认为8秒-----------'
    delay  = (float)(raw_input('间隔(秒): '))
    wanted = raw_input('选择你关注的课程(全部:0, 公选:1, 专选:2): ')
    if (delay <= 6.0 or delay >= 30.0):
        delay = 8.0
    if (wanted == '0'):
        wanted = '全部'
    elif (wanted == '1'):
        wanted = '公选'
    elif (wanted == '2'):
        wanted = '专选'
    sid = 0
    flag = 'y'
    user = {    'username' : getpass.getpass("Student ID: "),
                'password' : getpass.getpass("Password: "),
                'lt'       : '',
                '_eventId' : 'submit',
                'gateway'  : 'true'
           }
    while (flag == 'y'):
        if (sid == 0):
            flag = raw_input('开始?(y/n)')
            sid = login(user)
        else:
            print '---------------查询开始---------------'
            sid = course(sid, wanted)
            print '---------------查询结束---------------'
            flag = 'y'
            time.sleep(delay)

init()


        






