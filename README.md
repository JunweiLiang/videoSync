# videoSync

	1. Dependencies (known):
		(1) ffmpeg >= 2.2.4
		(2) sox >= v14.4.1
		(3) parallel
		(4) python 2.7
			a. numpy
			b. scipy

	2. Preparation:
		(1)  if your platform is not ubuntu, you may need to recompile assignKmeans.cpp to assignKmeans binary
		(2) since the file selected_stftabs_w100h50_0.4.txt.cluster_centres is big, you will need to download it manually from https://github.com/JunweiLiang/videoSync/blob/master/selected_stftabs_w100h50_0.4.txt.cluster_centres and put it in the same directory as the scripts.


	3. Example command:
		$ python master.py -videolst testVideos.lst -workPath videoSync_test -debug 
		Note: 
			(1) testVideos.lst is a text file containing each line an absolute path to a video.

	4. Output explanation

		Here I use 3 videos as input:
		x2wk58j_00:00:04.066_00:00:08.900.mp4
		43_00:00:00.033_00:00:27.766.mp4
		9.mp4

		After the code sucessfully run, under videoSync_test/ will includes (supposing you give k=3 videos as input):
			wav/   # you can delete this
			stft/  # this as well
			stft_con_w100h50/ # this as well
			kmeans_ass/ # this as well
			rankfiles/ # this includes pairwise synchronization results
			globalResult.txt  # this is the global synchronization result

		(1) pairwise synchronization result:
			under videoSync_test/rankfiles/ there will be k=3 files. Each file contains pairwise results of this video to the others. The content is like this:
			$ less rankfiles/9.txt
			43_00:00:00.033_00:00:27.766,1.6,46.0013920695,0.0,0.4
			x2wk58j_00:00:04.066_00:00:08.900,7.2,15.9063165656,0.8,0.4

			Each line's format is (videoname,offset,confidence_score,ignoreMe,ignoreMe). The first line means that for video 9.mp4 and 43_00:00:00.033_00:00:27.766.mp4: 43_00:00:00.033_00:00:27.766.mp4 should start playing for 1.6 seconds then 9.mp4 should start.

		(2) global synchronization result
			First of all, global synchronization result is not reliable as pairwise results. So use it at your discretion...

			What's inside?
			$ less globalResult.txt
			x2wk58j_00:00:04.066_00:00:08.900,0.0
			43_00:00:00.033_00:00:27.766,5.6
			9,7.2
			None,None

			This means that x2wk58j_00:00:04.066_00:00:08.900.mp4 should start first, then 5.6 seconds later, 43_00:00:00.033_00:00:27.766 should start playing... The "None,None" is a seperator for different group of synchronized videos.
