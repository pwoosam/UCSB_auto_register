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


def login(payload):
    '''
    Initializes session and logs you in.
    '''
    global session, resp
    url = "https://my.sa.ucsb.edu/gold/login.aspx"
    session = requests.Session()
    resp = session.get(url)

    soup = BeautifulSoup(resp.content, 'html.parser')
    payload["__EVENTVALIDATION"] = soup.find(id="__EVENTVALIDATION")['value']
    payload["__VIEWSTATE"] = soup.find(id="__VIEWSTATE")['value']
    payload["__VIEWSTATEGENERATOR"] = \
        soup.find(id="__VIEWSTATEGENERATOR")['value']

    resp = session.post(url, data=payload)


def navigate(page):
    '''
    Navigates throught the main pages.
    '''
    global session, resp
    pages = {"My Class Schedule": "ctl00$ctl05",
             "Registration Info": "ctl00$ctl09"}
    soup = BeautifulSoup(resp.content, 'html.parser')
    __VIEWSTATE = soup.find(id="__VIEWSTATE")['value']
    __VIEWSTATEGENERATOR = soup.find(id="__VIEWSTATEGENERATOR")['value']
    payload = {"__EVENTTARGET": pages[page],
               "__VIEWSTATE": __VIEWSTATE,
               "__VIEWSTATEGENERATOR": __VIEWSTATEGENERATOR}
    resp = session.post(resp.url, data=payload)


def nav_quarter(quarter=None):
    '''
    Changes quarter from dropdown menu.
    '''
    global session, resp
    seasons = {"winter": "1", "spring": "2", "summer": "3", "fall": "4"}
    if quarter is None:
        quarter = input("Enter quarter and year: ")
    season_year = quarter.split()
    season = seasons[season_year[0].lower()]
    year = season_year[1]
    quarter_code = year + season

    soup = BeautifulSoup(resp.content, 'html.parser')
    __VIEWSTATE = soup.find(id="__VIEWSTATE")['value']
    __VIEWSTATEGENERATOR = soup.find(id="__VIEWSTATEGENERATOR")['value']
    payload = {"__EVENTTARGET": "ctl00$pageContent$quarterDropDown",
               "__VIEWSTATE": __VIEWSTATE,
               "__VIEWSTATEGENERATOR": __VIEWSTATEGENERATOR,
               "ctl00$pageContent$quarterDropDown": quarter_code}
    resp = session.post(resp.url, data=payload)
    return quarter_code


def input_enrl_id_list():
    '''
    Asks the user for some course enrollment IDs
    '''
    enrl_ids = input("Enter course enrollment IDs, separated by spaces: ")
    enrl_id_list = enrl_ids.split()
    return enrl_id_list


def add_courses(enrl_id_list, quarter=None):
    '''
    Adds courses to your schedule by enrollment ID.
    '''
    global session, resp
    navigate("My Class Schedule")
    qtr_code = nav_quarter(quarter)
    for enrl_id in enrl_id_list:
        soup = BeautifulSoup(resp.content, 'html.parser')
        __VIEWSTATE = soup.find(id="__VIEWSTATE")['value']
        __VIEWSTATEGENERATOR = soup.find(id="__VIEWSTATEGENERATOR")['value']
        payload = {"__VIEWSTATE": __VIEWSTATE,
                   "__VIEWSTATEGENERATOR": __VIEWSTATEGENERATOR,
                   "ctl00$pageContent$quarterDropDown": qtr_code,
                   "ctl00$pageContent$EnrollCodeTextBox": enrl_id,
                   "ctl00$pageContent$addCourseButton.x": "34",
                   "ctl00$pageContent$addCourseButton.y": "12"}
        resp = session.post(resp.url, data=payload)

        soup = BeautifulSoup(resp.content, 'html.parser')
        __VIEWSTATE = soup.find(id="__VIEWSTATE")['value']
        __VIEWSTATEGENERATOR = soup.find(id="__VIEWSTATEGENERATOR")['value']
        payload.clear()
        payload = {"__VIEWSTATE": __VIEWSTATE,
                   "__VIEWSTATEGENERATOR": __VIEWSTATEGENERATOR,
                   "ctl00$pageContent$AddToScheduleButton.x": "63",
                   "ctl00$pageContent$AddToScheduleButton.y": "13"}
        resp = session.post(resp.url, data=payload)


def list_courses():
    '''
    Prints courses for a given quarter.
    '''
    global session, resp
    navigate("My Class Schedule")
    nav_quarter()
    soup = BeautifulSoup(resp.content, 'html.parser')
    course_titles = soup.find_all(id=re.compile("^pageContent_CourseList_\
CourseHeading"))
    for course in course_titles:
        print(course.string)


def get_pass_times(quarter=None):
    '''
    Returns a list of unformatted pass times for a given quarter
    '''
    global resp
    navigate("Registration Info")
    nav_quarter(quarter)
    soup = BeautifulSoup(resp.content, "html.parser")
    pass1 = soup.find(id="pageContent_PassOneLabel")
    pass2 = soup.find(id="pageContent_PassTwoLabel")
    pass3 = soup.find(id="pageContent_PassThreeLabel")
    pass_times = [pass1.string, pass2.string, pass3.string]
    print("Pass 1: {}\nPass 2: {}\nPass 3: {}"
          .format(pass_times[0], pass_times[1], pass_times[2]))
    return pass_times


def format_pass_times(pass_times):
    '''
    argument is an unformatted list of pass times
    returns a list of formatted pass time lists

    in: ["5/24/2016 6:15 PM - 5/31/2016 11:45 PM", ..., ...]
    out: [[datetime.datetime(2016, 5, 24, 18, 15),
          datetime.datetime(2016, 5, 24, 18, 15)],
          [..., ...], [..., ...]]
    '''
    formatted_dt = []
    for dt in pass_times:
        start_end = dt.split(" - ")
        start = datetime.strptime(start_end[0], "%m/%d/%Y %I:%M %p")
        end = datetime.strptime(start_end[1], "%m/%d/%Y %I:%M %p")
        formatted_dt.append([start, end])
    return formatted_dt


def pass_timer(formatted_dt, countdown=True):
    '''
    Loops until you are within one of your pass times
    '''
    passnum = [True, True, True]
    for pass_n, dt, i in zip(passnum, formatted_dt, range(3)):
        while pass_n:
            current_time = datetime.now()
            if current_time >= dt[0] and\
                    current_time < dt[1]:
                print("It's your pass time!")
                return 1
            elif current_time >= dt[1]:
                print("Pass {} has passed.".format(i + 1))
                pass_n = False
            else:
                timediff = dt[0] - current_time
                cur_time_str = current_time.strftime("%B %d, %Y %I:%M %p")
                print("Current date and time: {}".format(cur_time_str))
                print("Time until Pass {}: {}".format(i + 1, timediff))
                if countdown:
                    time.sleep(0.10)
                else:
                    time.sleep(timediff.total_seconds())

login_payload = {"ctl00$pageContent$userNameText": input("UCSB NetID: "),
                 "ctl00$pageContent$passwordText": getpass.getpass(),
                 "ctl00$pageContent$loginButton.x": "108",
                 "ctl00$pageContent$loginButton.y": "11"}
login(login_payload)
while True:
    choice = input("Display courses(1), register for courses(2) \
or exit(<enter>): ")
    if choice == "1":
        list_courses()
    elif choice == "2":
        quarter = input("Enter quarter and year: ")
        enrl_id_list = input_enrl_id_list()
        pass_times = get_pass_times(quarter)
        formatted_dt = format_pass_times(pass_times)
        pass_timer(formatted_dt, countdown=False)
        login(login_payload)
        add_courses(enrl_id_list, quarter)
    elif not choice:
        print("Goodbye")
        break
    else:
        print("ERROR: Not a valid choice")
