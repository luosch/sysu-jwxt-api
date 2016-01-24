# -*- coding:utf-8 -*-

from PIL import Image
import pytesseract
import requests
import hashlib
import demjson
from bs4 import BeautifulSoup


class Jwxt:
    def __init__(self, sno, password):
        """
        :param sno: eight bit student number, like '13331193'
        :param password: the corresponding password
        :return: a instance of JWXT api
        """
        self.session = requests.session()
        self.sno = sno
        self.password = hashlib.md5(password.encode('utf-8')).hexdigest().upper()
        self.grade = None
        self.tno = None
        self.headers = {
            'Host': 'uems.sysu.edu.cn',
            'Accept': '*/*',
            'ajaxRequest': 'true',
            'render': 'unieap',
            '__clientType': 'unieap',
            'workitemid': 'null',
            'resourceid': 'null',
            'Content-Type': 'multipart/form-data',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36'
        }

    def login(self):
        # get random number value and store cookie via session
        req = self.session.get(
            url='http://uems.sysu.edu.cn/jwxt',
            headers={'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36'}
        )
        soup = BeautifulSoup(req.content.decode('utf-8'), 'html.parser')
        rno = soup.find(id='rno')['value']

        # get verify_code using pytesseract
        req = self.session.get("http://uems.sysu.edu.cn/jwxt/jcaptcha", stream=True)
        im = Image.open(req.raw).convert('L')
        im = im.point(lambda x: 255 if x > 128 else x)
        im = im.point(lambda x: 0 if x < 255 else 255)
        box = (2, 2, im.size[0] - 2, im.size[1] - 2)
        im = im.crop(box)
        verify_code = pytesseract.image_to_string(im, lang="eng", config="-psm 7")
        verify_code = verify_code.replace(' ', '').strip()

        # try to login
        login_data = {
            "j_username": self.sno,
            "j_password": self.password,
            "jcaptcha_response": verify_code,
            "rno": rno
        }
        req = self.session.post(
            url="http://uems.sysu.edu.cn/jwxt/j_unieap_security_check.do",
            data=login_data
        )

        soup = BeautifulSoup(req.content.decode('utf-8'), 'html.parser')

        if req.status_code == 200:
            text = soup.find('title')
            if text and text.get_text() == u'首页':
                return False

            # get student info
            self.get_info()

            return True
        else:
            return False

    def get_info(self):
        """
        :set major number and grade
        """
        req = self.session.post(
            url='http://uems.sysu.edu.cn/jwxt/xscjcxAction/xscjcxAction.action?method=judgeStu',
            headers=self.headers,
            data='{header:{"code": -100, "message": {"title": "", "detail": ""}},body:{dataStores:{},parameters:{"args": [], "responseParam": "result"}}}'
        )
        res = demjson.decode(req.content.decode('utf-8'))
        info_list = res['body']['parameters']['result'].split(',')
        self.grade = info_list[1]
        self.tno = info_list[2]

    def get_course_list(self, xnd, xq):
        """
        :param xnd: year, eg. '2015-2016'
        :param xq: term, can be '1', '2', '3'
        :return: list contains course information
        """
        req = self.session.post(
            url='http://uems.sysu.edu.cn/jwxt/KcbcxAction/KcbcxAction.action?method=getList',
            headers=self.headers,
            data='{header:{"code": -100, "message": {"title": "", "detail": ""}},body:{dataStores:{},parameters:{"args": ["'+xq+'", "'+xnd+'"], "responseParam": "rs"}}}'
        )
        res = demjson.decode(req.content.decode('utf-8'))
        raw_html = res['body']['parameters']['rs']
        soup = BeautifulSoup(raw_html.encode('utf-8'), 'lxml')
        course_list = []
        for tr in soup.find_all('tr'):
            for index, td in enumerate(tr.find_all('td')):
                if td.has_attr('rowspan'):
                    raw = td.contents
                    course_list.append({
                        'courseName': raw[0],
                        'location': raw[2],
                        'day': index,
                        'time': raw[4].replace(u'节', ''),
                        'duration': raw[6]
                    })

        return course_list

    def get_score_list(self, xnd, xq):
        """
        :param xnd: year, eg. '2015-2016'
        :param xq: term, can be '1', '2', '3'
        :return: list contains scores for each course
        """
        req = self.session.post(
            url='http://uems.sysu.edu.cn/jwxt/xscjcxAction/xscjcxAction.action?method=getKccjList',
            headers=self.headers,
            data='{header:{"code": -100, "message": {"title": "", "detail": ""}},body:{dataStores:{kccjStore:{rowSet:{"primary":[],"filter":[],"delete":[]},name:"kccjStore",pageNumber:1,pageSize:10,recordCount:0,rowSetName:"pojo_com.neusoft.education.sysu.xscj.xscjcx.model.KccjModel",order:"t.xn, t.xq, t.kch, t.bzw"}},parameters:{"kccjStore-params": [{"name": "Filter_t.pylbm_0.7607312996540416", "type": "String", "value": "\''+'01'+'\'", "condition": " = ", "property": "t.pylbm"}, {"name": "Filter_t.xn_0.7704413492958447", "type": "String", "value": "\''+xnd+'\'", "condition": " = ", "property": "t.xn"}, {"name": "Filter_t.xq_0.40025491171181043", "type": "String", "value": "\''+xq+'\'", "condition": " = ", "property": "t.xq"}], "args": ["student"]}}}'
        )

        res = demjson.decode(req.content.decode('utf-8'))
        return res['body']['dataStores']['kccjStore']['rowSet']['primary']

    def get_gpa(self, xnd, xq):
        """
        :param xnd: year, eg. '2015-2016'
        :param xq: term, can be '1', '2', '3'
        :return: GPA of one term
        """
        req = self.session.post(
            url='http://uems.sysu.edu.cn/jwxt/xscjcxAction/xscjcxAction.action?method=getAllJd',
            headers=self.headers,
            data='{header:{"code": -100, "message": {"title": "", "detail": ""}},body:{dataStores:{jdStore:{rowSet:{"primary":[],"filter":[],"delete":[]},name:"jdStore",pageNumber:1,pageSize:0,recordCount:0,rowSetName:"pojo_com.neusoft.education.sysu.djks.ksgl.model.TwoColumnModel"}},parameters:{"args": ["'+self.sno + '", "' + xnd + '", "' + xq + '", ""]}}}'
        )
        res = demjson.decode(req.content.decode('utf-8'))
        return res['body']['dataStores']['jdStore']['rowSet']['primary']

    def get_all_gpa(self):
        """
        :return: GPA of all terms
        """
        req = self.session.post(
            url='http://uems.sysu.edu.cn/jwxt/xscjcxAction/xscjcxAction.action?method=getAllJd',
            headers=self.headers,
            data='{header:{"code": -100, "message": {"title": "", "detail": ""}},body:{dataStores:{allJdStore:{rowSet:{"primary":[],"filter":[],"delete":[]},name:"allJdStore",pageNumber:1,pageSize:2147483647,recordCount:0,rowSetName:"pojo_com.neusoft.education.sysu.djks.ksgl.model.TwoColumnModel"}},parameters:{"args": ["'+self.sno + '", "", "", ""]}}}'
        )
        res = demjson.decode(req.content.decode('utf-8'))
        return res['body']['dataStores']['allJdStore']['rowSet']['primary']

    def get_credit(self):
        """
        :return: credit already got
        """
        req = self.session.post(
            url='http://uems.sysu.edu.cn/jwxt/xscjcxAction/xscjcxAction.action?method=getAllXf',
            headers=self.headers,
            data='{header:{"code": -100, "message": {"title": "", "detail": ""}},body:{dataStores:{allJdStore:{rowSet:{"primary":[],"filter":[],"delete":[]},name:"allJdStore",pageNumber:1,pageSize:2147483647,recordCount:0,rowSetName:"pojo_com.neusoft.education.sysu.djks.ksgl.model.TwoColumnModel"}},parameters:{"args": ["'+self.sno + '", "", "", ""]}}}'
        )
        res = demjson.decode(req.content.decode('utf-8'))
        return res['body']['dataStores']['allJdStore']['rowSet']['primary']

    def get_total_credit(self):
        """
        :return: total credits needed for graduation
        """
        req = self.session.get(
            url='http://uems.sysu.edu.cn/jwxt/xscjcxAction/xscjcxAction.action?method=getZyxf',
            headers=self.headers,
            data='{header:{"code": -100, "message": {"title": "", "detail": ""}},body:{dataStores:{zxzyxfStore:{rowSet:{"primary":[],"filter":[],"delete":[]},name:"zxzyxfStore",pageNumber:1,pageSize:2147483647,recordCount:0,rowSetName:"pojo_com.neusoft.education.sysu.djks.ksgl.model.TwoColumnModel"}},parameters:{"zxzyxfStore-params": [{"name": "pylbm", "type": "String", "value": "\'01\'", "condition": " = ", "property": "x.pylbm"}, {"name": "nj", "type": "String", "value": "\''+self.grade+'\'", "condition": " = ", "property": "x.nj"}, {"name": "zyh", "type": "String", "value": "\''+self.tno+'\'", "condition": " = ", "property": "x.zyh"}], "args": []}}}'
        )
        res = demjson.decode(req.content.decode('utf-8'))
        return res['body']['dataStores']['zxzyxfStore']['rowSet']['primary']
