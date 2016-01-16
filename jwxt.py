# -*- coding:utf-8 -*-

from PIL import Image
import pytesseract
import requests
import hashlib
import demjson
from bs4 import BeautifulSoup


class Jwxt:
    def __init__(self, stuNum, password):
        """
        return a instance of JWXT api
        :param stuNum: eight bit student number, like '13331193'
        :param password: the corresponding password
        """
        self.session = requests.session()
        self.stuNum = stuNum
        self.password = hashlib.md5(password.encode('utf-8')).hexdigest().upper()

    def login(self):
        # get random number value and store cookie via session
        req = self.session.get(
            url='http://uems.sysu.edu.cn/jwxt',
            headers={'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36'}
        )
        soup = BeautifulSoup(req.content.decode('utf-8'), 'html.parser')
        rno = soup.find(id='rno')['value']

        # get verifyCode using pytesseract
        req = self.session.get("http://uems.sysu.edu.cn/jwxt/jcaptcha", stream=True)
        im = Image.open(req.raw).convert('L')
        im = im.point(lambda x:255 if x > 128 else x)
        im = im.point(lambda x:0 if x < 255 else 255)
        box = (2, 2, im.size[0] - 2, im.size[1] - 2)
        im = im.crop(box)
        verifyCode = pytesseract.image_to_string(im, lang="eng", config="-psm 7")
        verifyCode = verifyCode.replace(' ', '').strip()

        # try to login
        loginData = {
            "j_username": self.stuNum,
            "j_password": self.password,
            "jcaptcha_response": verifyCode,
            "rno": rno
        }
        req = self.session.post(
            url="http://uems.sysu.edu.cn/jwxt/j_unieap_security_check.do",
            data=loginData
        )
        soup = BeautifulSoup(req.content.decode('utf-8'), 'html.parser')
        if req.status_code == 200:
            text = soup.find('title')
            if text and text.get_text() == u'首页':
                return False
            return True
        else:
            return False

    def getCourseList(self, xq, xnd):
        """
        return a list contains course information
        :param xq: term, can be '1', '2', '3'
        :param xnd: year, eg. '2015-2016'
        """
        req = self.session.post(
            url='http://uems.sysu.edu.cn/jwxt/KcbcxAction/KcbcxAction.action?method=getList',
            headers={
                'Accept': '*/*',
                'ajaxRequest': 'true',
                'render': 'unieap',
                '__clientType': 'unieap',
                'workitemid': 'null',
                'resourceid': 'null',
                'Content-Type': 'multipart/form-data',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36'
            },
            data='{header:{"code": -100, "message": {"title": "", "detail": ""}},body:{dataStores:{},parameters:{"args": ["'+xq+'", "'+xnd+'"], "responseParam": "rs"}}}'
            # data={
            #     'header':{
            #         "code": -100,
            #         "message": {"title": "", "detail": ""}
            #     },
            #     'body':{
            #         'dataStores':{},
            #         'parameters':{
            #             'args': [xq, xnd],
            #             'responseParam': 'rs'
            #         }
            #     }
            # }
        )
        res = demjson.decode(req.content.decode('utf-8'))
        rawHTML = res['body']['parameters']['rs']
        soup = BeautifulSoup(rawHTML.encode('utf-8'), 'lxml')
        courseList = []
        for tr in soup.find_all('tr'):
            for index, td in enumerate(tr.find_all('td')):
                if td.has_attr('rowspan'):
                    raw = td.contents
                    courseList.append({
                        'courseName': raw[0],
                        'location': raw[2],
                        'day': index,
                        'time': raw[4].replace(u'节', ''),
                        'duration': raw[6]
                    })

        return courseList

    def getScoreList(self, xq, xnd):
        """
        return a list contains scores for each course
        :param xq: term, can be '1', '2', '3'
        :param xnd: year, eg. '2015-2016'
        """
        req = self.session.post(
            url='http://uems.sysu.edu.cn/jwxt/xscjcxAction/xscjcxAction.action?method=getKccjList',
            headers={
                'Accept': '*/*',
                'ajaxRequest': 'true',
                'render': 'unieap',
                '__clientType': 'unieap',
                'workitemid': 'null',
                'resourceid': 'null',
                'Content-Type': 'multipart/form-data',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36'
            },
            data='{header:{"code": -100, "message": {"title": "", "detail": ""}},body:{dataStores:{kccjStore:{rowSet:{"primary":[],"filter":[],"delete":[]},name:"kccjStore",pageNumber:1,pageSize:10,recordCount:0,rowSetName:"pojo_com.neusoft.education.sysu.xscj.xscjcx.model.KccjModel",order:"t.xn, t.xq, t.kch, t.bzw"}},parameters:{"kccjStore-params": [{"name": "Filter_t.pylbm_0.7607312996540416", "type": "String", "value": "\''+'01'+'\'", "condition": " = ", "property": "t.pylbm"}, {"name": "Filter_t.xn_0.7704413492958447", "type": "String", "value": "\''+xnd+'\'", "condition": " = ", "property": "t.xn"}, {"name": "Filter_t.xq_0.40025491171181043", "type": "String", "value": "\''+xq+'\'", "condition": " = ", "property": "t.xq"}], "args": ["student"]}}}'
        )

        res = demjson.decode(req.content.decode('utf-8'))
        return res['body']['dataStores']['kccjStore']['rowSet']['primary']