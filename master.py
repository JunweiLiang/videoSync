# coding=utf-8
# master script for video synchronization using audio

from ChunWai import *
import sys,os

def usage():
	print """
		-videolst : a txt file with all videos' absolute path
		-workPath : the path for all the temporary files. You can delete it later
		-debug : under this mode we will print out as much as possible
	"""
	sys.exit()

if __name__ == "__main__":
	videolst,workPath,debug = resolveParam(['-videolst','-workPath'],['-debug'])
	if(cp([videolst,workPath])):
		usage()
	workPath = parsePath(workPath)
	videos = [line.strip() for line in open(videolst,"r").readlines()]
	codePath = parsePath(os.path.dirname(os.path.realpath(__file__))) # where the master.py at , assuming the rest of the scripts are all here

	
	paraJob = 4 # so here I hardcoded how many parallel core to use

	# ignore these
	stft_con_w = 100
	stft_con_h = 50
	timeIs = 0.008*stft_con_h # 0.008 is the stft hop setting

	# all scripts path/ and some model
	getWav = codePath+'getWav.py'
	getStft = codePath+'wav2stft.py'
	stft_con = codePath+'stft_cat.py'
	kmeanscenter = codePath+'selected_stftabs_w100h50_0.4.txt.cluster_centres'
	kmeansbin = codePath+'assignKmeans'
	kmeans = codePath+'assignKmeans.py'
	sequenceMatching = codePath+'batchSequenceMatching.py'
	globalSync = codePath+'globalSync.py'

	# temp output path under workPath
	workPathWav = workPath+"wav/"
	workPathStft = workPath+"stft/"
	workPathStft_con = workPath+"stft_con_w%sh%s/"%(stft_con_w,stft_con_h)
	workPathKmeansAss = workPath+"kmeans_ass/"
	workPathRankfiles = workPath+"rankfiles/"
	globalResult = workPath+"globalResult.txt"
	#workPathCache = workPath+"cache/" # so we do not use cache, since if videos are over 100, will generate a large cache (hundreds of GB)
	mkdir(workPath)
	mkdir(workPathWav)
	mkdir(workPathStft)
	mkdir(workPathStft_con)
	mkdir(workPathKmeansAss)
	mkdir(workPathRankfiles)
	#mkdir(workPathCache)


	#run get wav first
	print "Step 1, getting wav..."
	cmd = "python %s -filelst %s -desp %s -skip"%(getWav,videolst,workPathWav)
	runParallel(cmd,paraJob,debug)

	#get stft
	print "Step 2, getting stft..."
	cmd = "python %s -wavp %s -stftpabs %s -skip"%(getStft,workPathWav,workPathStft)
	runParallel(cmd,paraJob,debug) # set to True to print the output of the script 

	#concatenating stft
	print "Step 3, concatenating stft..."
	output = commands.getoutput("python %s -stftp %s -newp %s -window %s -hop %s -skip"%(stft_con,workPathStft,workPathStft_con,stft_con_w,stft_con_h))

	# assign kmeans center
	print "Step 4, assigning audio signature..."
	cmd = "python %s -featp %s -desp %s -ctr %s -bin %s -skip"%(kmeans,workPathStft_con,workPathKmeansAss,kmeanscenter,kmeansbin)
	runParallel(cmd,paraJob,debug)

	print "Step 5, pairwise synchronization..."
	cmd = "python %s -seqp1 %s -seqp2 %s -t %s -rankp %s -skip"%(sequenceMatching,workPathKmeansAss,workPathKmeansAss,timeIs,workPathRankfiles)
	runParallel(cmd,paraJob,debug)

	print "Step 6, getting global synchronization result..."
	output = commands.getoutput("python %s -rankp %s -desFile %s -mergeChain"%(globalSync,workPathRankfiles,globalResult))
	