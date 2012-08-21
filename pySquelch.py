import datetime,pylab, numpy, time, os

def smoothListGaussian(list,degree=10):
        window=degree*2-1
        weight=numpy.array([1.0]*window)
        weightGauss=[]
        for i in range(window):
                i=i-degree+1
                frac=i/float(window)
                gauss=1/(numpy.exp((4*(frac))**2))
                weightGauss.append(gauss)
        weight=numpy.array(weightGauss)*weight
        smoothed=[0.0]*(len(list)-window)
        for i in range(len(smoothed)):
          smoothed[i]=sum(numpy.array(list[i:i+window])*weight)/sum(weight)
        while len(list)>len(smoothed)+int(window/2):
                smoothed.insert(0,None)
        while len(list)>len(smoothed):
				smoothed.append(None)
        return smoothed

def loadData(fname="squelchLog.txt",lastHour=True):
	print "extracting data...",
	global mins,vals
	f=open(fname)
	raw=f.read()
	f.close()
	mins,vals=[],[]
	for line in raw.split("\n"):
		if len(line)<3 or "---" in line: continue
		line = line.split(",")
		mins.append(datetime.datetime.fromtimestamp(int(line[0])))
		vals.append(int(line[1]))
	print "COMPLETE"
	return [mins,vals]
def barActivity(threshold,color,al):
	global mins,vals,smooth
	start=None
	for i in range(len(mins)-1):
		if smooth[i]>threshold:
			if start==None: start=mins[i]
		else:
			if start==None: continue
			pylab.axvspan(start,mins[i],fc=color,ec='none',alpha=al)
			start=None
	return

def graph():
	print "graphing:",
	global mins,vals,smooth
	smooth=smoothListGaussian(vals)
	fig=pylab.figure(figsize=(9,4))
	ax=pylab.subplot(111)
	print("allTime.png,"),
	pylab.title("147.120 MHz Activity (updated: %s)"%\
				str(datetime.datetime.now()).split(".")[0])
	barActivity(5,'k',.1)
	barActivity(50,'r',.2)
	pylab.grid(alpha=.3)
	pylab.plot(mins,vals,'k',alpha=.2,lw=1)
	pylab.plot(mins,smooth,'b')
	pylab.plot(mins,smoothListGaussian(vals,60),'g')
	fig.autofmt_xdate()
	pylab.ylabel("Seconds of Transmission per Minute")
	pylab.xlabel("All Time")
	pylab.axis([None,None,-5,65])
	fig.subplots_adjust(left=0.11, bottom=0.25, right=.98)
	#pylab.show()
	#raw_input()
	pylab.savefig("allTime.png",dpi=700./9.)
	print("lastHour.png,"),
	pylab.xlabel("Last Hour")
	pylab.axis([mins[-60],mins[-1],-5,65])
	pylab.savefig("lastHour.png",dpi=700./9.)
	print("lastDay.png,"),
	#pylab.xlabel("Last 24 Hours")
	#pylab.axis([mins[-(60*24)],mins[-1],-5,65])
	#pylab.savefig("lastDay.png",dpi=700./9.)
	print "COMPLETE"

def makeHTML():
	print "generating HTML output...",
	global mins,vals
	html="""<head><title>pySquelch Frequency Activity Analysis for:
 147.120MHz (Orlando, FL)</title><style type="text/css">
<!--
body {
font-size: 14px;
font-family: Verdana, Arial, SunSans-Regular, Sans-Serif;
text-align: center;
}
--></style></head><body><h2>pySquelch Frequency Activity Report for:<br>
147.120MHz (Orlando, FL)</h2><img src="lastHour.png"><br>
<img src="allTime.png"><br>
<table border=0 cellspacing=0 cellpadding=5 width=700 align="center">
<tr><td style="background: #AAAAAA">RECENT ACTIVITY</td></tr>
<tr><td style="background: #DDDDDD"><code>LINES</code></td></tr></table>
<br><table border=0 cellspacing=0 cellpadding=5 width=700 align="center">
<tr><td>
<b><a>pySquelch</a></b> Frequency Activity Analysis software was written
by <a href="mailto:SWHarden@gmail.com">Scott Harden</a>
(<a href="http://www.qrz.com/callsign?callsign=KJ4LDF">KJ4LDF</a>) and
<a href="mailto:fredeckert@hotmail.com">Fred Eckert</a> 
(<a href="http://www.qrz.com/callsign?callsign=KJ4LFJ">KJ4LFJ</a>) and 
can be downloaded from <a href="#">somewhere soon</a>.
</td></tr></table></body></html>
"""
	htmlTable=""
	mins2=mins
	if len(mins2)>60: mins2=mins[-60:]
	for i in range(len(mins2)):
		line="\nMinute <b>%s</b> experienced <b>%d</b>"%\
						(str(mins[i]),vals[i])
		line+=" seconds of transmission (%0.02f%% active)<br>"%\
						(float(vals[i])/60.0*100.0)
		htmlTable=line+htmlTable
	html=html.replace("LINES",htmlTable)
	f=open("pySquelch.html",'w')
	f.write(html)
	f.close()
	print "COMPLETE"

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
	#print "SEC:",sum(secA),
	return sum(secA)

def updateLog(deleteToo=True):
	print "checking for new slices..."
	files=os.listdir ('./')
	files.sort()
	processed=0
	for fname in files:
		if fname[-4:]==".raw" and "slice" in fname:
			processed+=1
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
				print "Processing",fileName,"...",
				logLine="%d,%d\n"%(secFile,analFile(fileName))
				f=open('squelchLog.txt','a')
				f.write(logLine)
				f.close()
				if deleteToo: 
					os.remove('./%s'%fname)
					print "logged and deleted"
				else: print "logged -- AND KEPT ON DISK?!"
	return processed


firstTime=True
while True:
	if updateLog()>0 or firstTime==True:
		print "re-plotting..."
		loadData()
		graph()
		makeHTML()
		firstTime=False
	print "sleeping...\n\n"
	time.sleep(30)