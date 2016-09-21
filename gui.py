from tkinter import *
from goldAutoReg import GOLD_browser
import sys


class print_to_text_box(object):
    def write(self, string):
        text_box.insert(END, string)


def login():
    br.login(user_value.get(), pass_value.get())


def list_courses():
    br.list_courses(quarter_value.get())
    text_box.insert(END, '\n')


def auto_enroll():
    def add_enrl_codes():
        br.enrl_code_list = enrl_codes_value.get().split()
    add_enrl_codes()
    br.get_pass_times(quarter_value.get())
    br.pass_timer(countdown=False)
    br.login()
    br.add_courses(quarter_value.get())
    text_box.insert(END, '\n')


sys.stdout = print_to_text_box()
br = GOLD_browser()

window = Tk()

# text box where all is printed
text_box = Text(window, width=100, height=15)
text_box.grid(row=1, column=0, rowspan=7, columnspan=5)

# button to list courses
list_courses_button = Button(window, text='List Courses', command=list_courses)
list_courses_button.grid(row=7, column=6)

# button to enroll in courses
auto_enroll_button = Button(window, text='Auto Enroll', command=auto_enroll)
auto_enroll_button.grid(row=6, column=6)

# field to enter quarter
quarter_value = StringVar()
quarter_entry = Entry(window, textvariable=quarter_value)
quarter_entry.grid(row=2, column=6, sticky=N)

# label for quarter field
quarter_label = Label(window, text='Enter quarter and year')
quarter_label.grid(row=1, column=6, sticky=S)

# field to enter enrollment codes
enrl_codes_value = StringVar()
enrl_codes_entry = Entry(window, textvariable=enrl_codes_value)
enrl_codes_entry.grid(row=4, column=6, sticky=N)

# label for enrollment codes field
enrl_codes_label = Label(window, text='Enter enrollment codes')
enrl_codes_label.grid(row=3, column=6, sticky=S)

# field to enter username
user_value = StringVar()
user_entry = Entry(window, textvariable=user_value)
user_entry.grid(row=0, column=1)

# label for username field
user_label = Label(window, text='UCSB NetID: ', width=10)
user_label.grid(row=0, column=0)

# field to enter username
pass_value = StringVar()
pass_entry = Entry(window, show='*', textvariable=pass_value)
pass_entry.grid(row=0, column=3)

# label for username field
pass_label = Label(window, text='Password: ')
pass_label.grid(row=0, column=2)

# button to login
login_button = Button(window, text='Login', command=login)
login_button.grid(row=0, column=4)

window.wm_title('UCSB Automatic Registration')
window.mainloop()
