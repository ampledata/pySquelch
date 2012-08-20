import pylab

def loadData():
        #returns Xs
        import time, datetime, pylab
        f=open('good.txt')
        raw=f.readlines()
        f.close()
        onTimes=[]
        timeStart=None
        lastOn=False
        for line in raw:
                if len(line)<10: continue
                line = line.strip('\n').split(" ")
                t=line[0]+" "+line[1]
                t=t.split('.')
                thisDay=time.strptime(t[0], "%Y-%m-%d %H:%M:%S")
                e=time.mktime(thisDay)+float("."+t[1])
                if timeStart==None: timeStart=e
                if line[-1]==1: stat=True
                else: stat=False
                if not lastOn and line[-1]=="1":
                        lastOn=e
                else:
                        onTimes.append([(lastOn-timeStart)/60.0,\
                                                        (e-timeStart)/60.0])
                        lastOn=False
        return onTimes

times = loadData()
pylab.figure(figsize=(8,3))
for t in times:
        pylab.fill([t[0],t[0],t[1],t[1]],[0,1,1,0],'k',lw=0,alpha=.5)
pylab.axis([None,None,-3,4])
pylab.title("A little QSO")
pylab.xlabel("Time (minutes)")
pylab.show()

