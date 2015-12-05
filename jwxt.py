# coding=utf-8

from PIL import Image
from PIL import ImageChops
import pytesseract
import requests
import hashlib
import json
from bs4 import BeautifulSoup

class jwxt:
    def __init__(self, stuNum, password):
        """
        return a instance of jwxt api
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