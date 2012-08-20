import time, datetime, os
import numpy

def analFile(fname):
	threshold=200 # set this to suit your audio levels
	dataY=numpy.memmap(fname, dtype='h', mode='r') #read PCM
	print "LEN:",len(dataY),
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
	print "SEC:",sum(secA),
	return sum(secA)


#print "I will analyze, log, and delete *.wav files >2 minutes old...\n"
while True:
	f=open('squelchLog.txt','a')
	f.write("--- NEW ENTRY ---\n")
	f.close()
	#print "DELETING LOG"
	#os.remove('squelchLog.txt')
	time.sleep(1)
	files=os.listdir ('./')
	files.sort()
	for fname in files:
		if fname[-4:]==".raw" and "slice" in fname:
			fileName=fname
			fname=fname.replace("slice-",'').split('.')[0]
			fTime=datetime.datetime(*time.strptime(fname,\
							"%Y%m%d_%H:%M:%S")[0:6])
			if fTime.second<30:
				fTime=fTime-datetime.timedelta(seconds=fTime.second)
			else:
				fTime=fTime+datetime.timedelta(seconds=60-fTime.second)
			secNow=int(time.mktime(datetime.datetime.now().timetuple()))
			secFile=int(time.mktime(fTime.timetuple()))
			diff=secNow-secFile
			if diff>60*2:
				# analyze (then delete) files over 2 minutes old
				print "PROCESSING",fileName,"...",
				logLine="%d,%d\n"%(secFile,analFile(fileName))
				f=open('squelchLog.txt','a')
				f.write(logLine)
				f.close()
				#os.remove('./%s'%fname)
				print #"DELETED"
	print "squelchLog.txt has been updated!"
	raw_input("perss ENTER to do it all again")
