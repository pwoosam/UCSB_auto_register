import requests
import time
import datetime
import getpass
from bs4 import BeautifulSoup
from datetime import datetime as dateTime


def login():
    '''
    Initializes session and logs you in.
    '''
    global session, resp
    url = "https://my.sa.ucsb.edu/gold/login.aspx"
    session = requests.Session()
    resp = session.get(url)

    soup = BeautifulSoup(resp.content, 'html.parser')
    __EVENTVALIDATION = soup.find(id="__EVENTVALIDATION")['value']
    __VIEWSTATE = soup.find(id="__VIEWSTATE")['value']
    __VIEWSTATEGENERATOR = soup.find(id="__VIEWSTATEGENERATOR")['value']
    payload = {"ctl00$pageContent$userNameText": input("UCSB NetID?: "),
               "ctl00$pageContent$passwordText": getpass.getpass(),
               "ctl00$pageContent$loginButton.x": "108",
               "ctl00$pageContent$loginButton.y": "11",
               "__EVENTVALIDATION": __EVENTVALIDATION,
               "__VIEWSTATE": __VIEWSTATE,
               "__VIEWSTATEGENERATOR": __VIEWSTATEGENERATOR}

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
        start = dateTime.strptime(start_end[0], "%m/%d/%Y %I:%M %p")
        end = dateTime.strptime(start_end[1], "%m/%d/%Y %I:%M %p")
        formatted_dt.append([start, end])
    return formatted_dt


def pass_timer(formatted_dt):
    '''
    Loops until you are within one of your pass times
    '''
    passnum = [True, True, True]
    while True:
        for i in range(len(formatted_dt)):
            while passnum[i]:
                current_time = dateTime.now()
                if current_time >= formatted_dt[i][0] and\
                        current_time < formatted_dt[i][1]:
                    print("It's your pass time!")
                    return 1
                elif current_time >= formatted_dt[i][1]:
                    passnum[i] = False
                else:
                    print(formatted_dt[i][0] - current_time)
                    time.sleep(0.1)


login()
pass_timer(format_pass_times(get_pass_times("Fall 2016")))
