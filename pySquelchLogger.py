import alsaaudio, time, audioop, datetime
inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE,alsaaudio.PCM_NONBLOCK)
inp.setchannels(1)
inp.setrate(4000)
inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)
inp.setperiodsize(1)

squelch = False
lastLog = 0
dataToLog = ""

def logIt(nowSquelch):
        global dataToLog, lastLog
        timeNow = datetime.datetime.now()
        epoch = time.mktime(timeNow.timetuple())
        if nowSquelch==True: nowSquelch=1
        else: nowSquelch=0
        logLine="%s %d\n"%(timeNow, nowSquelch)
        print timeNow, nowSquelch
        dataToLog+=logLine
        if epoch-lastLog>10:
                #print "LOGGING..."
                f=open('squelch.txt','a')
                f.write(dataToLog)
                f.close()
                lastLog = epoch
                dataToLog=""

while True:
        l,data = inp.read()
        if l:
                vol = audioop.max(data,2)
                #print vol #USED FOR CALIBRATION
                if vol>800: nowSquelch = True
                else: nowSquelch = False
                if not nowSquelch == squelch:
                        logIt(nowSquelch)
                        squelch = nowSquelch
        time.sleep(.01)

