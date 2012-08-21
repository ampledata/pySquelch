### CHANGE THESE VALUES ONLY ###############################

## working folder (location of audio files and output)
#workingPath="/var/www/pySquelch/" 
workingPath="/var/www/147120/stream-data/"

## for some reason different shading methods work on different PCs
# 0=off
# 1=works on scott's PC
# 2=works on fred's server
shadingMethod = 2

############################################################
## DON'T MODIFY BELOW THIS LINE UNLESS YOU ARE 100% SOBER ##
############################################################

print "GRAPHING: STARTING..."
print "importing libraries...",
import datetime, numpy, time, os
import matplotlib 
matplotlib.use("Agg")
import matplotlib.pyplot as plt
print "complete"

def smoothListGaussian(list,degree=10):
        # This is nice but slow [sigh] I'm not a great writer sometimes.
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
                        smoothed[i]=\
                        sum(numpy.array(list[i:i+window])*weight)/sum(weight)
        while len(list)>len(smoothed)+int(window/2):
                        smoothed.insert(0,None)
        while len(list)>len(smoothed):
                        smoothed.append(None)
        return smoothed

def loadData(fname):
        print "extracting data...",
        global mins,vals
        f=open(fname)
        raw=f.read()
        f.close()
        mins,vals=[],[]
        for line in raw.split("\n"):
                if len(line)<3 or "---" in line: continue
                line = line.split(",")
                thisMin=datetime.datetime.fromtimestamp(int(line[0]))
                if thisMin in mins:
                        if thisMin<mins[-1]: 
                                print("FOUND (IGNORING) DUPLICATE DATA!")
                else:
                        mins.append(thisMin)
                        vals.append(int(line[1]))
        print "COMPLETE"
        return [mins,vals]

def barActivity(threshold,color,al):
        global mins,vals,smooth
        start=None
        starts=[]
        if shadingMethod==0: return
        for i in range(len(smooth)-3600,len(smooth)-1):
                if smooth[i]>threshold:
                        if start==None: start=mins[i]
                else:
                        if start==None: continue
                        if  start in starts: continue
                        starts.append(start)
                        if shadingMethod==1:
                                plt.axvspan(start,mins[i],\
                                fc=color,ec='none',alpha=al)
                                #print start
                        if shadingMethod==2:
                                plt.subplot(111).fill([start,start,mins[i],\
                                mins[i]],[0,60,60,0],fc=color,ec='none',\
                                alpha=al)
                        start=None
        return

def graph():
        print "graphing:",
        global mins,vals,smooth
        smooth=smoothListGaussian(vals)
        fig=plt.figure(figsize=(9,4))
        ax=plt.subplot(111)
        print("allTime.png,"),
        plt.title("LAST MINUTE: 147.120 MHz Activity (updated: %s)"%\
                                str(datetime.datetime.now()).split(".")[0])
        plt.grid(alpha=.3)
        plt.plot(mins,vals,'k',alpha=.2,lw=1)
        plt.plot(mins[10:-10],smooth[10:-10],'b')
        plt.plot(mins[60:-60],smoothListGaussian(vals,60)[60:-60],'g')
        fig.autofmt_xdate()
        plt.ylabel("Seconds of Transmission per Minute")
        plt.xlabel("All Time")
        plt.axis([mins[0],mins[-1],0,60])
        fig.subplots_adjust(left=0.11, bottom=0.25, right=.98)
        #plt.show()
        #raw_input()
	plt.title("All Time: Activity Report")
        plt.savefig(workingPath+"allTime.png",dpi=700./9.)
        #barActivity(5,'k',.1)
        barActivity(50,'r',.2)
        #os.popen('convert %sallTime.png %sallTime.jpg'%\
        #         (workingPath,workingPath))
	plt.title("Last Hour: Activity Report")
        print("lastHour.png,"),
        plt.axis([mins[-60],mins[-1],-5,65])
        plt.savefig(workingPath+"lastHour.png",dpi=700./9.)
        #os.popen('convert %slastHour.png %slastHour.jpg'%(\
        #        workingPath,workingPath))
        print("lastDay.png,"),
        plt.xlabel("Last 24 Hours")
        plt.axis([mins[-(60*24)],mins[-1],-5,65])
	plt.title("Last 24 Hours: Activity report")
        plt.savefig(workingPath+"lastDay.png",dpi=700./9.)
        #os.popen('convert %slastDay.png %slastDay.jpg'%(\
        #        workingPath,workingPath))
        plt.close('all')
        print "COMPLETE"

def graphLastSound():
        threshold=200 # set this to suit your audio levels
        files=os.listdir(workingPath)
        files.sort()
        files2=[]
        for fname in files:
                if fname[-4:]==".raw" and "slice" in fname:
                        files2.append(fname)
        print "graphing", files2[0],"...",
        dataY=numpy.memmap(workingPath+fname, dtype='h', mode='r') #read PCM
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
        fig=plt.figure(figsize=(9,4))
        plt.subplot(211)
        plt.grid(alpha=.5)
        plt.title("LAST MINUTE: Trace of "+files2[0])
        plt.plot(dataX,dataY)
        plt.axis([0,60,None,None])
        plt.subplot(212)
        plt.grid(alpha=.5)
        plt.plot(secX,secY,label='Average Audio Intensity / Second')
        plt.plot([secX[0],secX[-1]],\
                 [threshold,threshold],'k--',label='threshold')
        plt.axis([0,60,None,None])
        plt.savefig(workingPath+"lastClip.png",dpi=700./9.)
        plt.close('all')
        #os.popen('convert %slastClip.png %slastClip.jpg'%\
        #         (workingPath,workingPath))
        print "complete"

def makeHTML():
        print "generating HTML output...",
        global mins,vals
        html="""<head><meta HTTP-EQUIV='Refresh' CONTENT='60'>
<title>pySquelch Frequency Activity Analysis for:
 147.120MHz (Orlando, FL)</title><style type="text/css">
<!--
body {
font-size: 14px;
font-family: Verdana, Arial, SunSans-Regular, Sans-Serif;
text-align: center;
}
--></style></head><body><h2>pySquelch Frequency Activity Report for:
<br>147.120MHz (Orlando, FL)</h2>
<img src="lastClip.png"><br>
<img src="lastHour.png"><br>
<img src="lastDay.png"><br>
<img src="allTime.png"><br>
<table border=0 cellspacing=0 cellpadding=5 width=700 align="center">
<tr><td style="background: #AAAAAA">RECENT ACTIVITY</td></tr>
<tr><td style="background: #DDDDDD"><code>LINES</code></td></tr></table>
<br>
<table border=0 cellspacing=0 cellpadding=5 width=700 align="center">
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
        for i in range(len(mins)-60,len(mins)-1):
                line="\nMinute <b>%s</b> experienced <b>%d</b>"%\
                                                (str(mins[i]),vals[i])
                line+=" seconds of transmission (%0.02f%% active)<br>"%\
                                                (float(vals[i])/60.0*100.0)
                htmlTable=line+htmlTable
        html=html.replace("LINES",htmlTable)
        f=open(workingPath+"pySquelch.html",'w')
        f.write(html)
        f.close()
        print "COMPLETE"

loadData(workingPath+"squelchLog.txt")
graph()
graphLastSound()
makeHTML()
time.sleep(3)
print "GRAPHING: COMPLETE!"

