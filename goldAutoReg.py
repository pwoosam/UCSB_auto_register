#!/usr/bin/env python3
#
# UCSB Auto Registration Copyright (C) 2016, Patrick Woo-Sam
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import requests
import time
import getpass
import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

__author__ = "Patrick Woo-Sam"
__email__ = "pwoosam5@icloud.com"
__copyright__ = "UCSB Auto Registration Copyright (C) 2016, Patrick Woo-Sam"
__license__ = "GNU GPL"


class GOLD_browser():
    def __init__(self):
        self.username = None
        self.password = None
        self.session = requests.Session()
        self.resp = None
        self.pass_times = None
        self.enrl_code_list = None

    def login(self, username=None, password=None):
        '''
        Initializes session and logs you in.
        '''
        if self.username is None or self.password is None:
            self.username = username
            self.password = password

        assert self.username is not None and self.password is not None, \
            "Username and password not set!"
        payload = {"ctl00$pageContent$userNameText": self.username,
                   "ctl00$pageContent$passwordText": self.password,
                   "ctl00$pageContent$loginButton.x": "108",
                   "ctl00$pageContent$loginButton.y": "11"}

        url = "https://my.sa.ucsb.edu/gold/login.aspx"
        self.resp = self.session.get(url)

        soup = BeautifulSoup(self.resp.content, 'html.parser')
        payload["__EVENTVALIDATION"] = \
            soup.find(id="__EVENTVALIDATION")['value']
        payload["__VIEWSTATE"] = soup.find(id="__VIEWSTATE")['value']
        payload["__VIEWSTATEGENERATOR"] = \
            soup.find(id="__VIEWSTATEGENERATOR")['value']

        self.resp = self.session.post(url, data=payload)

    def navigate(self, page):
        '''
        Navigates throught the main pages.
        '''
        pages = {"My Class Schedule": "ctl00$ctl05",
                 "Registration Info": "ctl00$ctl09"}
        soup = BeautifulSoup(self.resp.content, 'html.parser')
        __VIEWSTATE = soup.find(id="__VIEWSTATE")['value']
        __VIEWSTATEGENERATOR = soup.find(id="__VIEWSTATEGENERATOR")['value']
        payload = {"__EVENTTARGET": pages[page],
                   "__VIEWSTATE": __VIEWSTATE,
                   "__VIEWSTATEGENERATOR": __VIEWSTATEGENERATOR}
        self.resp = self.session.post(self.resp.url, data=payload)

    def nav_quarter(self, quarter=None):
        '''
        Changes quarter from dropdown menu.
        '''
        seasons = {"winter": "1", "spring": "2", "summer": "3", "fall": "4"}
        if quarter is None:
            quarter = input("Enter quarter and year: ")
        season_year = quarter.split()
        season = seasons[season_year[0].lower()]
        year = season_year[1]
        quarter_code = year + season

        soup = BeautifulSoup(self.resp.content, 'html.parser')
        __VIEWSTATE = soup.find(id="__VIEWSTATE")['value']
        __VIEWSTATEGENERATOR = soup.find(id="__VIEWSTATEGENERATOR")['value']
        payload = {"__EVENTTARGET": "ctl00$pageContent$quarterDropDown",
                   "__VIEWSTATE": __VIEWSTATE,
                   "__VIEWSTATEGENERATOR": __VIEWSTATEGENERATOR,
                   "ctl00$pageContent$quarterDropDown": quarter_code}
        self.resp = self.session.post(self.resp.url, data=payload)
        return quarter_code

    def input_enrl_code_list(self):
        '''
        Asks the user for some course enrollment IDs
        '''
        enrl_codes = input("Enter course enrollment codes, \
separated by spaces: ")
        enrl_code_list = enrl_codes.split()
        self.enrl_code_list = enrl_code_list

    def add_courses(self, quarter=None):
        '''
        Adds courses to your schedule by enrollment ID.
        '''
        self.navigate("My Class Schedule")
        qtr_code = self.nav_quarter(quarter)
        for enrl_code in self.enrl_code_list:
            soup = BeautifulSoup(self.resp.content, 'html.parser')
            __VIEWSTATE = soup.find(id="__VIEWSTATE")['value']
            __VIEWSTATEGENERATOR = soup.find(id="__VIEWSTATEGENERATOR")['value']
            payload = {"__VIEWSTATE": __VIEWSTATE,
                       "__VIEWSTATEGENERATOR": __VIEWSTATEGENERATOR,
                       "ctl00$pageContent$quarterDropDown": qtr_code,
                       "ctl00$pageContent$EnrollCodeTextBox": enrl_code,
                       "ctl00$pageContent$addCourseButton.x": "34",
                       "ctl00$pageContent$addCourseButton.y": "12"}
            self.resp = self.session.post(self.resp.url, data=payload)

            soup = BeautifulSoup(self.resp.content, 'html.parser')
            __VIEWSTATE = soup.find(id="__VIEWSTATE")['value']
            __VIEWSTATEGENERATOR = soup.find(id="__VIEWSTATEGENERATOR")['value']
            payload.clear()
            payload = {"__VIEWSTATE": __VIEWSTATE,
                       "__VIEWSTATEGENERATOR": __VIEWSTATEGENERATOR,
                       "ctl00$pageContent$AddToScheduleButton.x": "63",
                       "ctl00$pageContent$AddToScheduleButton.y": "13"}
            self.resp = self.session.post(self.resp.url, data=payload)
            print("Course {} added".format(enrl_code))

    def list_courses(self, quarter=None):
        '''
        Prints courses for a given quarter.
        '''
        self.navigate("My Class Schedule")
        self.nav_quarter(quarter)
        soup = BeautifulSoup(self.resp.content, 'html.parser')
        course_titles = soup.find_all(id=re.compile("pageContent_CourseList_\
CourseHeading"))
        for course in course_titles:
            print(course.string)

    def get_pass_times(self, quarter=None):
        '''
        Prints pass times and populates GOLD_browser.pass_times
        '''
        self.navigate("Registration Info")
        self.nav_quarter(quarter)
        soup = BeautifulSoup(self.resp.content, "html.parser")
        pass1 = soup.find(id="pageContent_PassOneLabel")
        pass2 = soup.find(id="pageContent_PassTwoLabel")
        pass3 = soup.find(id="pageContent_PassThreeLabel")
        prnt_pass_times = [pass1.string, pass2.string, pass3.string]

        self.pass_times = []
        for i, pass_time in enumerate(prnt_pass_times):
            start_end = pass_time.split(" - ")
            start = datetime.strptime(start_end[0], "%m/%d/%Y %I:%M %p")
            end = datetime.strptime(start_end[1], "%m/%d/%Y %I:%M %p")
            self.pass_times.append([start, end])

        print("Pass 1: {}\nPass 2: {}\nPass 3: {}"
              .format(prnt_pass_times[0], prnt_pass_times[1],
                      prnt_pass_times[2]))

    def pass_timer(self, countdown=True):
        '''
        Loops until you are within one of your pass times
        '''
        passnum = [True, True, True]
        for pass_n, dt, i in zip(passnum, self.pass_times, range(3)):
            while pass_n:
                current_time = datetime.now()
                if current_time >= dt[0] and\
                        current_time < dt[1]:
                    print("It's your pass time!")
                    return
                elif current_time >= dt[1]:
                    print("Pass {} has passed.".format(i + 1))
                    pass_n = False
                else:
                    timediff = dt[0] - current_time
                    cur_time_str = current_time.strftime("%B %d, %Y %I:%M %p")
                    if countdown:
                        print("Current date and time: {}".format(cur_time_str))
                        print("Time until Pass {}: {}".format(i + 1, timediff))
                    time.sleep(0.10)

if __name__ == '__main__':
    br = GOLD_browser()
    br.login(input("UCSB NetID: "), getpass.getpass())
    while True:
        choice = input("Display courses(1), register for courses(2) \
or exit(<enter>): ")
        if choice == "1":
            br.list_courses()
        elif choice == "2":
            quarter = input("Enter quarter and year: ")
            br.input_enrl_code_list()
            br.get_pass_times(quarter)
            br.pass_timer(countdown=False)
            br.login()
            br.add_courses(quarter)
        elif not choice:
            print("Goodbye")
            break
        else:
            print("ERROR: Not a valid choice")
