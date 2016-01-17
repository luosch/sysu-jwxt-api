# -*- coding:utf-8 -*-

from jwxt import Jwxt
from config import TEST_STUNUM, TEST_PASSWORD

def main():
    test = Jwxt(TEST_STUNUM, TEST_PASSWORD)
    test.login()

    for credit in test.getCredit():
        print credit['oneColumn'], credit['twoColumn']

    for gpa in test.getAllGPA():
        print gpa['oneColumn'], gpa['twoColumn']

    for gpa in test.getGPA('2015-2016', '1'):
        print gpa['oneColumn'], gpa['twoColumn']

    for course in test.getCourseList('2015-2016', '3'):
        print course['courseName']

    for score in test.getScoreList('2015-2016', '1'):
        print score['kcmc'], score['xf'], score['jd'], score['zzcj']


if __name__ == '__main__':
    main()
