# -*- coding:utf-8 -*-

from jwxt import JWXT
from config import *

def main():
    test1 = JWXT(TEST_STUNUM, TEST_PASSWORD)
    test1.login()
    coures_list = test1.getCourseList('3', '2015-2016')
    print len(coures_list)

if __name__ == '__main__':
    main()
