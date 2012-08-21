### CHANGE THESE VALUES ONLY ###############################

## delete .raw files after analysis? (True=yes, False=no)
#deleteJunk=False
deleteJunk=True

## working folder (location of audio files and output)
#workingPath="/var/www/pySquelch/" 
workingPath="/var/www/147120/stream-data/"

############################################################
## DON'T MODIFY BELOW THIS LINE UNLESS YOU ARE 100% SOBER ##
############################################################

print "importing libraries...",
import datetime, numpy, time, os, sys
print "complete"
sys.path.append(workingPath)

def analFile(fname):
        threshold=200 # set this to suit your audio levels
        dataY=numpy.memmap(fname, dtype='h', mode='r') #read PCM
        #print "LEN:",len(dataY),
        dataY=dataY-numpy.average(dataY) #adjust the sound vertically
        dataY=numpy.absolute(dataY) #no negative values
        valsPerSec=float(len(dataY)/60) #assume audio is 60 seconds long
        dataX=numpy.arange(len(dataY))/(valsPerSec) #time axis from 0 to 60
        secY,secX,secA=[],[],[]
        for sec in xrange(60):
                secData=dataY[valsPerSec*sec:valsPerSec*(sec+1)]
                val=numpy.average(secData)
                secY.append(val)
                secX.append(sec)
                if val>threshold: secA.append(1)
                else: secA.append(0)
        return sum(secA)

def updateLog(workingPath,deleteJunk):
        if deleteJunk==True:
                print "*SET TO DELETE AUDIO FILES ANALYSIS!*"
                for i in range(10):
                        print 10-i,'...'
                        time.sleep(1)
        print "checking for new slices..."
        deleteToo=deleteJunk
        files=os.listdir (workingPath)
        files.sort()
        processed=0
        fileCount=0
        for fname in files:
                if fname[-4:]==".raw" and "slice" in fname:
                        processed+=1
                        fileName=fname
                        fname=fname.replace("slice-",'').split('.')[0]
                        if ":" in fname: fname=fname.replace(":","-")
                        fTime=datetime.datetime(*time.strptime(fname,\
                                "%Y%m%d_%H-%M-%S")[0:6])
                        if fTime.second<30:
                                fTime=fTime-datetime.timedelta(\
                                        seconds=fTime.second)
                        else:
                                fTime=fTime+datetime.timedelta(\
                                        seconds=60-fTime.second)
                        secNow=int(time.mktime(\
                                datetime.datetime.now().timetuple()))
                        secFile=int(time.mktime(fTime.timetuple()))
                        diff=secNow-secFile
                        if diff>60*2:
                                print "Processing",fileName,"...",
                                logLine="%d,%d\n"%(secFile,\
                                        analFile(workingPath+fileName))
                                f=open(workingPath+'squelchLog.txt','a')
                                f.write(logLine)
                                f.close()
                                if deleteToo: 
                                        os.remove(workingPath+fileName)
                                        print "logged and deleted"
                                else: print "logged -- AND KEPT ON DISK?!"
                                print " --GRAPHING --"
                                import pySquelch_graph
                                print " -- DONE GRAPHING --"
        return processed

print "\nLOG ANALYSIS: STARTING"
updateLog(workingPath,deleteJunk)
print "LOG ANALYSIS: COMPLETE"
print "exiting...",
for i in range(3):
        print 3-i,
        time.sleep(1)

