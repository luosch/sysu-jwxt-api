# coding=utf-8

from jwxt import jwxt
from config import *

def main():
    test1 = jwxt(TEST_STUNUM, TEST_PASSWORD)
    test1.login()

if __name__ == '__main__':
    main()
