#/usr/bin/python3

"""Sinch SMS GUI

This script will build a GUI to use when sending SMS messages to Sinch

Program currently only supports sending calls to NANPA numbers

Will check for two files, sinch_sms.conf and numbers.txt by default.  If
those files exist the data will be imported into the GUI.  All fields in
the sinch_sms.conf file are optional and can be excluded if not used

sinch_sms.conf contents:
api-key = <sinch api key>
sms-url = <sinch sms url>
frm-num = <number to send from>

numbers.txt contents:
<put to numbers here - one number per line>

Python "requests" is required to be installed for SMS sending to work

File contains the following:

    * class SinchGui - builds the GUI
    * function main - main function of the script
    * function readConfigFile - gets the config variables from sinch_sms.conf
"""

# Imports
from sys import argv
from time import sleep
from os import listdir
import tkinter as tk
from tkinter import messagebox
import SinchSendSMS as SendSMS
import MessLog

# Global variables
SMS_URL = "https://us.sms.api.sinch.com/xms/v1/"
API_KEY = ""
FROM_NUMBER = ""
SINCH_VER = "1.2"
SMS_LOG = MessLog.MessLog(dirPrepend = '', filename = 'SMSGUI')

# default status message
status = "Input API key and numbers"

# Help message
helpmessage = "Sinch SMS GUI " + SINCH_VER + "\n\nDefault config file is sinch_sms.conf.  \
You can specify a different config file \
by using -c config-file-name when \
executing the program.  The program will \
also attempt to import a file called \
number.txt which should contain a default list \
of numbers to send the text to.  You can \
specify a different number list by using \
-n file-name when executing the program.  \
You can put numbers into lists with a .num \
extension to be able to load those numbers \
using the drop down menu.\n\
You will need an API Key from sinch.com \
in order to utilize the program."

class SinchGUI(tk.Frame):
    '''Create Sinch SMS GUI by extending tk.Frame'''
    def __init__(self, master = None):
        '''Constructor to build GUI window

        :param master: GUI window root
        :type master: tk.tk() object
        :returns: none
        '''
        # Call init from tk.Frame
        super().__init__(master)
        # Create GUI root and pack
        self.master = master
        self.pack()
        # instance variables
        self.SMS_URL = SMS_URL
        self.API_KEY = API_KEY
        self.FROM_NUMBER = FROM_NUMBER
        self.number_list = ['       Pick From Dropdown       ']
        # Populate number_list by finding and loading .num files
        for list_files in listdir('.'):
            poss_nums = list_files.split('.num')
            if len(poss_nums) == 2:
                self.number_list.append(poss_nums[0])
        # Variables for dropdown list
        self.number_list_var = tk.StringVar(self.master)
        self.number_list_var.set(self.number_list[0])
        # Create all GUI elements
        self.create_menu()
        self.create_api()
        self.create_sms_url()
        self.create_from_number()
        self.create_number_menu()
        self.create_to_numbers()
        self.create_text_message()
        self.create_run_button()
        self.create_status_line()
        self._update_status_line(status)
    
    def create_menu(self):
        ''' Creates the top menu
        '''
        menu = tk.Menu(self.master)

        aboutMenu = tk.Menu(menu)
        aboutMenu.add_command(label="About", command=self._display_about)
        menu.add_cascade(label="About", menu=aboutMenu)

        exitMenu = tk.Menu(menu)
        exitMenu.add_command(label="Exit", command=self._exit_app)
        menu.add_cascade(label="Exit", menu=exitMenu)

        self.master.config(menu=menu)

    def _exit_app(self):
        ''' Exits GUI
        '''
        self.master.quit()

    def _display_about(self):
        ''' Show messagebox with help message
        '''
        tk.messagebox.showinfo("About", helpmessage)

    def create_api(self):
        '''Create API Key label and entry field
        '''
        self.api_label = tk.Label(text = "Enter API Key")
        self.api_entry = tk.Entry(width = 50)
        self.api_label.pack()
        self.api_entry.pack()
        self.api_entry.insert(0, self.API_KEY)
    
    def create_sms_url(self):
        '''Create SMS URL label and entry field
        '''
        self.sms_url_label = tk.Label(text = "Enter SMS URL")
        self.sms_url_entry = tk.Entry(width = 50)
        self.sms_url_label.pack()
        self.sms_url_entry.pack()
        self.sms_url_entry.insert(0, self.SMS_URL)
    
    def create_from_number(self):
        '''Create From Number label and entry field
        '''
        self.from_num_label = tk.Label(text = "Enter From Number")
        self.from_num_entry = tk.Entry(width = 50)
        self.from_num_label.pack()
        self.from_num_entry.pack()
        self.from_num_entry.insert(0, self.FROM_NUMBER)
    
    def _load_numbers(self, choice):
        '''Load numbers from number list into to box
        '''
        choice = self.number_list_var.get()
        # If No selection is made do nothing
        if choice == '       Pick From Dropdown       ':
            pass
        # Clear the to_number textbox then fill with entries from .num file
        else:
            self.to_numbers_entry.delete("1.0", tk.END)
            add_numbers_file(choice + ".num")

    def create_number_menu(self):
        '''Create Drop down list for loading numbers
        '''
        number_list = self.number_list
        self.number_menu_label = tk.Label(text = "Select to Load Numbers From Lists")
        self.number_menu = tk.OptionMenu(self.master, self.number_list_var, *number_list, command=self._load_numbers)
        self.number_menu_label.pack()
        self.number_menu.pack()

    def create_to_numbers(self):
        '''Create To numbers label and entry text box
        '''
        self.to_numbers_frame = tk.Frame(width = 336, height = 100)
        self.to_numbers_frame.pack()
        self.to_numbers_label = tk.Label(master = self.to_numbers_frame, text = "Enter To Number(s)")
        self.to_numbers_entry = tk.Text(master = self.to_numbers_frame, height = 10, width = 35)
        self.to_scrollbar = tk.Scrollbar(master = self.to_numbers_frame, command = self.to_numbers_entry.yview)
        self.to_numbers_entry['yscrollcommand'] = self.to_scrollbar.set
        self.to_numbers_label.pack()
        self.to_scrollbar.pack(side = "right", fill = "y")
        self.to_numbers_entry.pack(side = "right")
    
    def create_text_message(self):
        '''Create text message label and entry text box
        '''
        self.text_message_frame = tk.Frame(width = 336, height = 50)
        self.text_message_frame.pack()
        self.text_message_label = tk.Label(master = self.text_message_frame, text = "Enter Text Message to Send - 140 character limit")
        self.text_message_entry = tk.Text(master = self.text_message_frame, height = 5, width = 35)
        self.text_message_scrollbar = tk.Scrollbar(master = self.text_message_frame, command = self.text_message_entry.yview)
        self.text_message_entry['yscrollcommand'] = self.text_message_scrollbar.set
        self.text_message_label.pack()
        self.text_message_scrollbar.pack(side = "right", fill = "y")
        self.text_message_entry.pack(side = "right")
    
    def create_run_button(self):
        '''Create run button
        '''
        self.run_button = tk.Button(text = "Send SMS", command = self.run_button)
        self.run_button.pack()
    
    def create_status_line(self):
        '''Create status line label and entry field
        '''
        self.status_line = tk.Entry(width = 50, state = 'disabled')
        self.status_label = tk.Label(text = "Status:")
        self.status_space = tk.Label(text = "")
        self.status_space.pack(side = "bottom")
        self.status_line.pack(side = "bottom")
        self.status_label.pack(side = "bottom")
    
    def _update_status_line(self, status = None):
        '''Method to update the status line
        :param status: string to update the status line with
        :type status: str
        :returns: none
        '''
        if status == None:
            pass
        else:
            self.status_line.config(state = 'normal')
            self.status_line.delete(0, tk.END)
            self.status_line.insert(0, status)
            self.status_line.config(state = 'readonly')
    
    def _copy(self, event=None):
        '''Execute copy when <ctrl-c> is pressed in a window
        :param event: listener event
        :type event: str listener
        :returns: none
        '''
        self.clipboard_clear()
        text = self.get("sel.first", "sel.last")
        self.clipboard_append(text)
    
    def _cut(self, event):
        '''Execute cut when <ctrl-x> is pressed in a window
        :param event: listener event
        :type event: str listener
        :returns: none
        '''
        self.copy()
        self.delete("sel.first", "sel.last")

    def _paste(self, event):
        '''Execute paste when <ctrl-v> is pressed in a window
        :param event: listener event
        :type event: str listener
        :returns: none
        '''
        text = self.selection_get(selection='CLIPBOARD')
        self.insert('insert', text)
    
    def run_button(self):
        '''Method that executes when run button is pressed
        '''
        global SMS_LOG
        numSentMsg = 0
        self.run_button.config(state = 'disabled')
        self._update_status_line(status = "Sending SMS message(s)")
        if  self.api_entry.get() == "":
            self._update_status_line(status = "Error! No API KEY specified")
            self.run_button.config(state = 'normal')
            return()
        else:
            pass
        if  self.sms_url_entry.get() == "":
            self._update_status_line(status = "Error! No SMS URL specified")
            self.run_button.config(state = 'normal')
            return()
        else:
            pass
        if  self.from_num_entry.get() == "":
            self._update_status_line(status = "Error! No FROM number specified")
            self.run_button.config(state = 'normal')
            return()
        else:
            pass
        to_numbers_list = self.to_numbers_entry.get("1.0", tk.END)
        if  to_numbers_list == "\n":
            self._update_status_line(status = "Error! No TO number specified")
            self.run_button.config(state = 'normal')
            return()
        else:
            pass
        text_message_list = self.text_message_entry.get("1.0", tk.END)
        if  text_message_list == "\n":
            self._update_status_line(status = "Error! No TEXT message specified")
            self.run_button.config(state = 'normal')
            return()
        else:
            if len(text_message_list.replace("\n", " ").strip()) > 140:
                self._update_status_line(status = "Error! TEXT message is " + str(len(text_message_list.replace("\n", " ").strip()) % 140) + " characters too long")
                self.run_button.config(state = 'normal')
                return()
        for number in to_numbers_list.splitlines():
            try:
                newnumber = int(number.strip())
            except ValueError:
                self._update_status_line(status = "Invalid number " + number + " in number list!")
                continue
            if (len(number) == 10):
                while (SendSMS.NUMTHREADS > SendSMS.ALLOWEDTHREADS):
                    SMS_LOG.writeLogFile("Over Allowed Threads!  Waiting for threads to free up...")
                    sleep(1)
                SendSMS.SendSMS(self.from_num_entry.get(), "1" + number, text_message_list.replace("\n", " ").strip(), self.sms_url_entry.get(), self.api_entry.get()).start()
                numSentMsg += 1
            elif (len(number) == 11) and (number[0] == "1"):
                while (SendSMS.NUMTHREADS > SendSMS.ALLOWEDTHREADS):
                    SMS_LOG.writeLogFile("Over Allowed Threads!  Waiting for threads to free up...")
                    sleep(1)
                SendSMS.SendSMS(self.from_num_entry.get(), number, text_message_list.replace("\n", " ").strip(), self.sms_url_entry.get(), self.api_entry.get()).start()
                numSentMsg += 1
            else:
                self._update_status_line(status = "Invalid number " + number + " in number list!")
                continue
        while SendSMS.threading.activeCount() > 1:
            sleep(1)
        self._update_status_line(status = str(numSentMsg) + " Text Message(s) sent!")
        self.run_button.config(state = 'normal')
    
def readConfigFile(configOption):
    '''Load items from config file into global variables
        :param configOption: string with line from config file
        :returns: none
    '''
    if "api-key=" in configOption:
        global API_KEY
        API_KEY = configOption[8:]
    if "sms-url=" in configOption:
        global SMS_URL
        SMS_URL = configOption[8:]
    if "from-num=" in configOption:
        global FROM_NUMBER
        FROM_NUMBER = configOption[9:]

def add_numbers_file(num_file_in):
    '''Adds numbers from file into to_numbers text box
        :param num_file_in: file to get numbers from
        :return: none
    '''
    try:
        with open(num_file_in) as numbers_file:
            for line in numbers_file.readlines():
                SinchApp.to_numbers_entry.insert(tk.END, line)
        SMS_LOG.writeLogFile("Loaded numbers from file: " + num_file_in + "\r\n")
    except FileNotFoundError:
        SMS_LOG.writeLogFile("File Not Found: " + num_file_in + "\r\n")
    except Exception as e:
        SMS_LOG.writeLogFile("Error reading NUMBERS_IN file: " + str(e) + "\r\n")
        exit()

# Begin Main execution
if __name__ == "__main__":
    SMS_CONFIG = "sinch_sms.conf"
    NUMBERS_IN = "numbers.txt"
    # Check execution for command line variables
    if len(argv) > 1:
        if len(argv) == 2:
            tk.messagebox.showinfo("Help", helpmessage)
            exit()
        elif (len(argv) == 3) and (str(argv[1]) == "-c"):
                SMS_CONFIG = str(argv[2])
        elif (len(argv) == 3) and (str(argv[1]) == "-n"):
                NUMBERS_IN = str(argv[2])
        elif (len(argv) == 5) and ((str(argv[1]) == "-c") and (str(argv[3]) == "-n")):
                SMS_CONFIG = str(argv[2])
                NUMBERS_IN = str(argv[4])
        elif (len(argv) == 5) and ((str(argv[1]) == "-n") and (str(argv[3]) == "-c")):
                SMS_CONFIG = str(argv[4])
                NUMBERS_IN = str(argv[2])
        else:
            tk.messagebox.showinfo("Help", helpmessage)
            exit()
    else:
        SMS_CONFIG = "sinch_sms.conf"
        NUMBERS_IN = "numbers.txt"

    # see if default config file exists and if so call readConfigFile function
    try:
        with open(SMS_CONFIG) as config_file:
            for line in config_file.readlines():
                readConfigFile(line.strip().replace(" ", ""))
    except FileNotFoundError:
        pass
    except Exception as e:
        SMS_LOG.writeLogFile("Error reading SMS_CONFIG file: " + str(e) + "\r\n")
        exit()
    
    # Create GUI root
    appRoot = tk.Tk()
    
    # Instantiate GUI
    SinchApp = SinchGUI(master = appRoot)
    SinchApp.master.title("Sinch SMS GUI")
    SinchApp.master.geometry("336x525")
    SinchApp.master.minsize(336, 525)
    SinchApp.master.maxsize(336, 525)
    
    # Add default numbers file
    add_numbers_file(NUMBERS_IN)
    
    # Execute GUI loop
    SinchApp.mainloop()