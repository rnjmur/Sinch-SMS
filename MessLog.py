#!/usr/bin/python3

#import time
from time import strftime, localtime

class MessLog():
    ''' Class to get last message time from file to see if a new message should be sent 
    '''
    def __init__(self, dirPrepend = '', filename = ''):
        ''' Initalize object with the directory prepend and name of file 
        '''
        self.dirPrepend = dirPrepend
        self.filename = filename
        self.setLogFile(dirPrepend = self.dirPrepend, filename = self.filename)

    def readLogTime(self):
        ''' Method to read the log time then return the timestamp 
        '''
        try:
            f = open(self.filename, 'r')
            sendtime = float(f.read()) + 1200
            f.close()
        except IOError:
            sendtime = 0
        except:
            sendtime = -1
        # return the timestamp
        return sendtime

    def writeLogTime(self, ts):
        ''' Method to write new timestamp to log file 
        '''
        try:
            f = open(self.filename, 'w')
            f.write(str(ts))
            f.close()
        except:
            pass
    
    def writeLogFile(self, message):
        ''' Method to write debug to log file.  All in variables must be strings 
        '''
        try:
            f = open(self.filename, 'a')
            f.write('Log Time: ' + strftime("%H:%M:%S", localtime()) + ' - ')
            f.write(message)
            f.write('\n')
            f.close()
        except:
            print('Error making Log file')
    
    def writeDebugFile(self, lasttimestamp, newtimestamp, messagereq, debugResp1='', debugResp2='', debugResp3=''):
        ''' Method to write debug to log file.  All in variables must be strings 
        '''
        try:
            f = open(self.debugfile, 'a')
            f.write('Log Time: ' + strftime("%H:%M:%S", localtime()) + '\r\n')
            f.write('Message Requested: ' + messagereq + '\r\n')
            f.write('Next Message Send Timestamp: ' + lasttimestamp + '\r\n')
            f.write('Current Timestamp: ' + newtimestamp + '\r\n')
            f.write(debugResp1 + '\r\n')
            f.write(debugResp2 + '\r\n')
            f.write(debugResp3 + '\r\n\r\n')
            f.close()
        except:
            print('Error making Debug file')
    
    def setLogFile(self, dirPrepend = '', filename = ''):
        self.filename = dirPrepend + strftime("%b-%d-%y", localtime()) + "-" + filename + '.log'
        self.debugfile = dirPrepend + strftime("%b-%d-%y", localtime()) + 'debug-SMS-trigger' + '.log'
