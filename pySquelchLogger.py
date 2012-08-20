#pySquelchLogger.py
import time, random, alsaaudio, audioop
inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE,alsaaudio.PCM_NONBLOCK)
inp.setchannels(2)
inp.setrate(1000)
inp.setformat(alsaaudio.PCM_FORMAT_S8)
inp.setperiodsize(100)
addToLog=""
lastLogTime=0

testLevel=False ### SET THIS TO 'True' TO TEST YOUR SOUNDCARD

def getVolEach():
        # this is a quick way to detect activity.
        # modify this function to use alternate methods of detection.
        while True:
                l,data = inp.read() # poll the audio device
                if l>0: break
        vol = audioop.max(data,1) # get the maximum amplitude
        if testLevel: print vol
        if vol>10: return True ### SET THIS NUMBER TO SUIT YOUR NEEDS ###
        return False

def getVol():
        # reliably detect activity by getting 3 consistant readings.
        a,b,c=True,False,False
        while True:
                a=getVolEach()
                b=getVolEach()
                c=getVolEach()
                if a==b==c:
                        if testLevel: print "RESULT:",a
                        break
        if a==True: time.sleep(1)
        return a

def updateLog():
        # open the log file, append the new data, and save it again.
        global addToLog,lastLogTime
        #print "UPDATING LOG"
        if len(addToLog)>0:
                f=open('log.txt','a')
                f.write(addToLog)
                f.close()
                addToLog=""
        lastLogTime=time.mktime(time.localtime())

def findSquelch():
        # this will record a single transmission and store its data.
        global addToLog
        while True: # loop until we hear talking
                time.sleep(.5)
                if getVol()==True:
                        start=time.mktime(time.localtime())
                        print start,
                        break
        while True: # loop until talking stops
                time.sleep(.1)
                if getVol()==False:
                        length=time.mktime(time.localtime())-start
                        print length
                        break
        newLine="%d,%d "%(start,length)
        addToLog+=newLine
        if start-lastLogTime>30: updateLog() # update the log

while True:
        findSquelch()

