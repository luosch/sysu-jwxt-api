# -*- coding:utf-8 -*-

from jwxt import Jwxt
from config import TEST_STUNUM, TEST_PASSWORD


def main():
    test = Jwxt(TEST_STUNUM, TEST_PASSWORD)
    test.login()
    test.get_info()

    # for credit in test.get_credit():
    #     print credit['oneColumn'], credit['twoColumn']

    # print '-' * 50

    # for credit in test.get_total_credit():
    #     print credit['oneColumn'], credit['twoColumn']

    # print '-' * 50

    # for gpa in test.get_gpa('2015-2016', '1'):
    #     print gpa['oneColumn'], gpa['twoColumn']

    # print '-' * 50

    for course in test.get_course_list('2015-2016', '3'):
        print course['course_name'], course['day']

    # print '-' * 50

    # for score in test.get_score_list('2015-2016', '1'):
    #     print score['kcmc'], score['xf'], score['jd'], score['zzcj']


if __name__ == '__main__':
    main()
