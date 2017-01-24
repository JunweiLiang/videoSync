# coding=utf-8
# sequence file to matching
# each line in sequence file is same to feature file.
# each line correspond to time
# each line's 'label' is a fingerprint, ha

import os,sys,operator,scipy#,cv2
import numpy as np
from ChunWai import *

def usage():
	print """
		-src
		-des
		-sp # whether each label in each line of sequence file is the same priority
		-t :time pos of a point, stft is 0.008 s, 0.008* hop is t
	"""
	sys.exit()

# given two filename, two matrix, one matrix, one filename?
# should be two dict?
class SeqMatch:
	def __init__(self,src,des,sp=False):
		self.src = src # sample file
		self.des = des # looking at file name
		self.sp = sp # whether each label in each line of sequence file is the same priority
		# loading in the label dictionary
		# dict[label] = [{"time":timeIndex(1~n),"p":priority(1~k)}]
		self.srcDict,self.srcTime = self.loadDict(filename=src)
		self.desDict,self.desTime = self.loadDict(filename=des)
		

	def loadDict(self,filename):
		dicti = {}
		countTime=0
		with open(filename,"r") as f:
			for line in f:
				countTime+=1
				if(line.strip() == ""):
					continue
				labels = line.strip().split(" ")
				for i in xrange(len(labels)):
					if(not dicti.has_key(labels[i])):
						dicti[labels[i]] = []
					if(self.sp):
						dicti[labels[i]].append({"time":countTime,"p":1})
					else:
						dicti[labels[i]].append({"time":countTime,"p":i+1})
		#for one in dicti.keys():
		#	dicti[one].sort(key=operator.itemgetter("p"))
		if(countTime == 0):
			error("error, countTime zero for %s"%filename)
		return dicti,countTime

	def match(self):
		#fill in a matching matrix.
		matchs = np.zeros((self.srcTime,self.desTime))

		pri = 35 # within what priority will be counted (1~k)
		srcDict = self.srcDict
		#print srcDict
		#sys.exit()
		desDict = self.desDict
		for srcFingerPrint in srcDict.keys():
			if(desDict.has_key(srcFingerPrint)):
				#mark all the time that such fingerprint occur
				for i in xrange(len(srcDict[srcFingerPrint])):
					for j in xrange(len(desDict[srcFingerPrint])):
						srcUnit = srcDict[srcFingerPrint][i]
						desUnit = desDict[srcFingerPrint][j]
						if((srcUnit['p'] <= pri) and (desUnit["p"] <= pri)):
							matchs[srcUnit['time']-1,desUnit['time']-1]+= (1.0/srcUnit['p'])*(1.0/desUnit['p'])
		return matchs

if __name__ == "__main__":
	import matplotlib.pyplot as plt
	src,des,t,sp = resolveParam(["-src","-des",'-t'],['-sp'])
	if(cp([src,des])):
		usage()
	#t
	Match = SeqMatch(src,des,sp=sp)
	matching = Match.match()
	#matching[matching < 0.5] = 0
	# get score peaks?
	"""stupid idea
	neighnms = 16
	row,col = matching.shape
	for i in xrange(row-neighnms+1):
		for j in xrange(col-neighnms+1):
			patch = matching[i:i+neighnms-1,j:j+neighnms-1]
			localmax = patch.max()
			patch[patch < localmax] = 0
	"""

	
	#plt.imshow(matching,cmap="coolwarm")
	#plt.colorbar()

	"""
	plt.imsave("test.jpg",matching,cmap=plt.cm.gray)
	gray = plt.imread("test.jpg")

	edges = cv2.Canny(gray,0,150,apertureSize = 3)
	plt.imshow(edges)
	plt.show()
	minLineLength = 1
	maxLineGap = 1000
	lines = cv2.HoughLinesP(edges,1,np.pi/180,100,minLineLength,maxLineGap)
	print lines
	"""
	
	"""
	# if the matched is too few, use this to see
	time_idx = []
	freq_idx = []
	for i in xrange(matching.shape[0]):
		for j in xrange(matching.shape[1]):
			if(matching[i,j]>0):
				time_idx.append(j)
				freq_idx.append(i)
	plt.scatter(time_idx,freq_idx)
	"""
	#plt.show()
	plt.imshow(matching,cmap="coolwarm")
	plt.colorbar()
	plt.show()
	#sys.exit()
	sleep(0.1)
	from hough import hough
	h = hough(matching)
	matchingh,offset = h.run()
	# get time differences,
	timeDiff = np.argmax(matchingh)+offset
	argmaxIndex = np.argmax(matchingh)
	evidence = h.evidence[argmaxIndex]
	value,endIndex,length = evidence
	startIndex = endIndex - length +1
	#print (timeDiff+49)*0.4
	# get the sored index of matchingh value
	max2minIndex = np.argsort(matchingh)[::-1]
	#print np.argmax(matchingh),max2minIndex[0]
	#max value bigger than second how much?
	if(matchingh[max2minIndex[1]] == 0):
		gap = 0.0
	else:
		#gap = (matchingh[max2minIndex[0]] - matchingh[max2minIndex[1]])/matchingh[max2minIndex[1]]
		gap = (matchingh[max2minIndex[0]] - matchingh[max2minIndex[1]])/matchingh[max2minIndex[1]]

	if(t!=""):
		t = float(t)
		timeDiff = timeDiff*t
	else:
		t = 1
	print "After %s has played %s +-%s,%s started; \nmax is second's %.4f times more \n max hough value/timeFrame is %.4f" % (os.path.basename(des),timeDiff,t,os.path.basename(src),gap,matchingh[argmaxIndex])
	if(timeDiff>0):
		print " after %s has started %s, the evidence start and last for %s seconds" %(os.path.basename(src),startIndex*t,length*t)
	else:
		print " after %s has started %s, the evidence start and last for %s seconds" %(os.path.basename(des),startIndex*t,length*t)
	#import operator
	#h.evidence.sort(key=operator.itemgetter(0))
	#print h.evidence[np.argmax(matchingh)]
	
	plt.bar(range(len(matchingh)),matchingh)
	plt.show()
	sleep(0.1)
	plt.imshow(matching,cmap="coolwarm")
	plt.plot([np.argmax(matchingh)+offset,np.argmax(matchingh)+offset+matching.shape[0]], [0, matching.shape[0]], 'k-')
	plt.show()

