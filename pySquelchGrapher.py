#pySquelchGrapher.py
print "loading libraries...",
import pylab, datetime, numpy
print "complete"

def loadData(fname="log.txt"):
        print "loading data...",
        # load signal/duration from log file
        f=open(fname)
        raw=f.read()
        f.close()
        raw=raw.replace('\n',' ')
        raw=raw.split(" ")
        signals=[]
        for line in raw:
                if len(line)<3: continue
                line=line.split(',')
                sec=datetime.datetime.fromtimestamp(int(line[0]))
                dur=int(line[1])
                signals.append([sec,dur])
        print "complete"
        return signals

def findDays(signals):
        # determine which days are in the log file
        print "finding days...",
        days=[]
        for signal in signals:
                day = signal[0].date()
                if not day in days:
                        days.append(day)
        print "complete"
        return days

def genMins(day):
        # generate an array for every minute in a certain day
        print "generating bins...",
        mins=[]
        startTime=datetime.datetime(day.year,day.month,day.day)
        minute=datetime.timedelta(minutes=1)
        for i in xrange(60*60):
                mins.append(startTime+minute*i)
        print "complete"
        return mins

def fillMins(mins,signals):
        print "filling bins...",
        vals=[0]*len(mins)
        dayToDo=signals[0][0].date()
        for signal in signals:
                if not signal[0].date() == dayToDo: continue
                sec=signal[0]
                dur=signal[1]
                prebuf = sec.second
                minOfDay=sec.hour*60+sec.minute
                if dur+prebuf<60: # simple case, no rollover seconds
                        vals[minOfDay]=dur
                else: # if duration exceeds the minute the signal started in
                        vals[minOfDay]=60-prebuf
                        dur=dur+prebuf
                        while (dur>0): # add rollover seconds to subsequent minutes
                                minOfDay+=1
                                dur=dur-60
                                if dur< =0: break
                                if dur>=60: vals[minOfDay]=60
                                else: vals[minOfDay]=dur
        print "complete"
        return vals

def normalize(vals):
        print "normalizing data...",
        divBy=float(max(vals))
        for i in xrange(len(vals)):
                vals[i]=vals[i]/divBy
        print "complete"
        return vals

def smoothListGaussian(list,degree=10):
        print "smoothing...",
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
                smoothed.insert(0,smoothed[0])
        while len(list)>len(smoothed):
                smoothed.append(smoothed[0])
        print "complete"
        return smoothed

signals=loadData()
days=findDays(signals)
for day in days:
        mins=genMins(day)
        vals=normalize(fillMins(mins,signals))
        fig=pylab.figure()
        pylab.grid(alpha=.2)
        pylab.plot(mins,vals,'k',alpha=.1)
        pylab.plot(mins,smoothListGaussian(vals),'b',lw=1)
        pylab.axis([day,day+datetime.timedelta(days=1),None,None])
        fig.autofmt_xdate()
        pylab.title("147.120 MHz Usage for "+str(day))
        pylab.xlabel("time of day")
        pylab.ylabel("fractional usage")
        pylab.show()

