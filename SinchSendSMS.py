#!/usr/bin/python3

from multiprocessing import cpu_count
import threading
import requests
import MessLog

ALLOWEDTHREADS = cpu_count()
NUMTHREADS = 0

class SendSMS(threading.Thread):
    ''' Class that creates an object to send SMS message  '''
    APIKEY = ''
    SMSURL = ''
    SMSFROM = ''
    SMSTO = ''

    def __init__(self, SMSFROM, SMSTO, smsText, SMSURL, APIKEY, debug=0):
        ''' Initaialize object with smsText value and create instance variables  '''
        threading.Thread.__init__(self)
        self.debug = debug
        self.SMS_LOG = MessLog.MessLog(dirPrepend = '', filename = 'SMSSend')
        self.SMSFROM = SMSFROM
        self.SMSTO = SMSTO
        self.SMSTEXT = smsText
        self.SMSURL = SMSURL
        self.APIKEY = APIKEY
        self.headers = {
        'Authorization': 'Bearer ' + self.APIKEY,
        'Content-Type': 'application/json',
        }
        
        self.data = '{"from": "'+self.SMSFROM+'",    "to": [ "'+self.SMSTO+'" ],    "body": "'+self.SMSTEXT+'" }'

    def run(self):
        ''' Send message to SMS provider  '''
        global NUMTHREADS
        NUMTHREADS += 1
        try:
            response = requests.post(self.SMSURL, headers=self.headers, data=self.data)
            # The below is for debugging
            if self.debug == 1:
                print(response.history)
                print(response.text)
                print(response)
            if str(response) != '<Response [201]>':
                self.SMS_LOG.writeLogFile("Error Sending SMS Message: " + str(response))
                self.SMS_LOG.writeLogFile(str(self.headers) + " " + str(self.data))
            # return response as a string
            return(response)
        except Exception as e:
            self.SMS_LOG.writeLogFile("Error in run thread: " + str(e))
        finally:
            NUMTHREADS -= 1
