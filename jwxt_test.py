# -*- coding:utf-8 -*-

from jwxt import Jwxt
from config import TEST_STUNUM, TEST_PASSWORD

def main():
    test1 = Jwxt(TEST_STUNUM, TEST_PASSWORD)
    test1.login()
    course_list = test1.getCourseList('3', '2015-2016')

    for course in course_list:
        print course['courseName']

    for score in test1.getScoreList('1', '2015-2016'):
        print score['kcmc'], score['xf'], score['jd'], score['zzcj']

if __name__ == '__main__':
    main()
