import datetime,pylab
def loadData(fname="squelchLog.txt",lastHour=True):
	f=open(fname)
	raw=f.read()
	f.close()
	mins,vals=[],[]
	for line in raw.split("\n"):
		if len(line)<3 or "---" in line: continue
		line = line.split(",")
		mins.append(datetime.datetime.fromtimestamp(int(line[0])))
		vals.append(int(line[1]))
	return [mins,vals]
	
### LOAD DATA ###

mins,vals=loadData()

### PLOT OF ALL TIME ###
fig=pylab.figure(figsize=(9,4))
ax=pylab.subplot(111)
pylab.title("Analysis of squelchLog.txt by grapher.py [updated: %s]"%\
			str(datetime.datetime.now()).split(".")[0])
pylab.grid(alpha=.3)
pylab.plot(mins,vals)
fig.autofmt_xdate()
pylab.ylabel("Seconds of Transmission per Minute")
pylab.axis([None,None,-5,65])
pylab.savefig("allTime.png",dpi=700./9.)
pylab.close()

### PLOT OF LAST HOUR ###
fig=pylab.figure(figsize=(9,4))
if len(mins)>60:
	mins=mins[-60:]
	vals=vals[-60:]
ax=pylab.subplot(111)
pylab.title("Analysis of squelchLog.txt by grapher.py [updated: %s]"%\
			str(datetime.datetime.now()).split(".")[0])
pylab.grid(alpha=.3)
pylab.plot(mins,vals)
fig.autofmt_xdate()
locs, labels = pylab.xticks()
locs2, labels2=[],[]
for i in range(len(locs)):
	if i%5==0:
		labels2.append(labels[i])
		locs2.append(locs[i])
pylab.xticks(locs2)
pylab.ylabel("Seconds of Transmission per Minute")
pylab.axis([None,None,-5,65])
pylab.savefig("lastHour.png",dpi=700./9.)
pylab.close()

### DUMP TABLE FOR LAST HOUR ###
f=open("pySquelch_template.html")
html=f.read()
f.close()
htmlTable=""
for i in range(len(mins)):		
	htmlTable+="\nMinute <b>%s</b> experienced <b>%d</b>"%\
					(str(mins[i]),vals[i])
	htmlTable+=" seconds of transmission (%0.02f%% active)<br>"%\
					(float(vals[i])/60.0*100.0)
html=html.replace("LINES",htmlTable)
f=open("index.html",'w')
f.write(html)
f.close()
