import requests
import time
import getpass
import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


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
             "Find Courses": "",
             "Registration Info": "ctl00$ctl09",
             "Grades": "",
             "Academic History": "",
             "Transcripts/Verification": ""}  # some not yet added
    soup = BeautifulSoup(resp.content, 'html.parser')
    __VIEWSTATE = soup.find(id="__VIEWSTATE")['value']
    __VIEWSTATEGENERATOR = soup.find(id="__VIEWSTATEGENERATOR")['value']
    payload = {"__EVENTTARGET": pages[page],
               "__VIEWSTATE": __VIEWSTATE,
               "__VIEWSTATEGENERATOR": __VIEWSTATEGENERATOR}
    resp = session.post(resp.url, data=payload)


def nav_quarter(quarter):
    '''
    Changes quarter from dropdown menu.
    '''
    global session, resp
    season_year = quarter.split()
    year = season_year[1]
    seasons = {"Winter": "1", "Spring": "2", "Summer": "3", "Fall": "4"}
    season = seasons[season_year[0]]
    quarter_code = year + season

    soup = BeautifulSoup(resp.content, 'html.parser')
    __VIEWSTATE = soup.find(id="__VIEWSTATE")['value']
    __VIEWSTATEGENERATOR = soup.find(id="__VIEWSTATEGENERATOR")['value']
    payload = {"__EVENTTARGET": "ctl00$pageContent$quarterDropDown",
               "__VIEWSTATE": __VIEWSTATE,
               "__VIEWSTATEGENERATOR": __VIEWSTATEGENERATOR,
               "ctl00$pageContent$quarterDropDown": quarter_code}
    resp = session.post(resp.url, data=payload)


def input_enrl_id_list():
    '''
    Asks the user for some course enrollment IDs
    '''
    enrl_ids = input("Enter course enrollment IDs, separated by spaces: ")
    enrl_id_list = enrl_ids.split()
    return enrl_id_list


def add_courses(enrl_id_list):
    '''
    Adds courses to your schedule by enrollment ID.
    '''
    global session, resp
    navigate("My Class Schedule")
    for enrl_id in enrl_id_list:
        soup = BeautifulSoup(resp.content, 'html.parser')
        __VIEWSTATE = soup.find(id="__VIEWSTATE")['value']
        __VIEWSTATEGENERATOR = soup.find(id="__VIEWSTATEGENERATOR")['value']
        payload = {"__VIEWSTATE": __VIEWSTATE,
                   "__VIEWSTATEGENERATOR": __VIEWSTATEGENERATOR,
                   "ctl00$pageContent$enrollmentCodeTextBox": enrl_id,  # need to verify
                   "ctl00$pageContent$addButton.x": "",  # need to verify / find
                   "ctl00$pageContent$addButton.y": ""}  # need to verify / find
        resp = session.post(resp.url, data=payload)

        soup = BeautifulSoup(resp.content, 'html.parser')
        __VIEWSTATE = soup.find(id="__VIEWSTATE")['value']
        __VIEWSTATEGENERATOR = soup.find(id="__VIEWSTATEGENERATOR")['value']
        payload.clear()
        payload = {"__VIEWSTATE": __VIEWSTATE,
                   "__VIEWSTATEGENERATOR": __VIEWSTATEGENERATOR,
                   "ctl00$pageContent$addToScheduleButton.x": "",  # need to verify / find
                   "ctl00$pageContent$addToScheduleButton.y": ""}  # need to verify / find


def list_courses(quarter):
    '''
    Prints courses for a given quarter.
    '''
    global session, resp
    navigate("My Class Schedule")
    nav_quarter(quarter)
    soup = BeautifulSoup(resp.content, 'html.parser')
    course_titles = soup.find_all(id=re.compile("^pageContent_CourseList_\
CourseHeading"))
    for course in course_titles:
        print(course.string)


def get_pass_times(quarter):
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
    for i in range(len(formatted_dt)):
        while passnum[i]:
            current_time = datetime.now()
            if current_time >= formatted_dt[i][0] and\
                    current_time < formatted_dt[i][1]:
                print("It's your pass time!")
                return 1
            elif current_time >= formatted_dt[i][1]:
                print("Pass {} has passed.".format(i + 1))
                passnum[i] = False
            else:
                timediff = formatted_dt[i][0] - current_time
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
        quarter = input("Enter quarter and year: ")
        list_courses(quarter)
    elif choice == "2":
        quarter = input("Enter quarter and year: ")
        enrl_id_list = input_enrl_id_list()
        pass_times = get_pass_times(quarter)
        formatted_dt = format_pass_times(pass_times)
        pass_timer(formatted_dt, countdown=False)
        login(login_payload)
        add_courses(enrl_id_list)
    else:
        print("Goodbye")
        break
