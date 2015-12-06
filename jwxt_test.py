# coding=utf-8

from jwxt import JWXT
from config import *

def main():
    test1 = JWXT(TEST_STUNUM, TEST_PASSWORD)
    test1.login()
    print test1.getCourseList('2', '2015-2016')

if __name__ == '__main__':
    main()
